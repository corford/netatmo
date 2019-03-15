/* 
  This gulpfile is a quick & dirty port from v3 to v4.
  TO DO: needs a complete re-factor when time permits
*/
import {spawn} from "child_process";
import del from "del";
import log from "fancy-log";
import pluginError from "plugin-error";
import hugo from "hugo-bin";
import merge2 from "merge2";
import gulp from "gulp";
import hash from "gulp-hash";
import concat from "gulp-concat";
import flatten from "gulp-flatten";
import filter from "gulp-filter";
import sourceMaps from "gulp-sourcemaps";
import gulpif from "gulp-if";
import sass from "gulp-sass";
import postcss from "gulp-postcss";
import autoprefixer from "autoprefixer";
import cssnano from "cssnano";
import cssImport from "postcss-import";
import postcssPresetEnv from "postcss-preset-env";
import gulpWebpack from "webpack-stream";
import webpack from "webpack";
import webpackConfig from "./webpack.conf";
import BrowserSync from "browser-sync";

const hugoArgsCommon = [
  "-s", "site",
  "-b", (process.env.HUGO_BASE_URL) ? process.env.HUGO_BASE_URL : "/",
  "-v"
];

const hugoArgsStandard = ["-d", "../dist",];
const hugoArgsPreview = ["-d", "../dist_preview", "--buildDrafts", "--buildFuture"];
const browserSync = BrowserSync.create();

// Compile CSS and SASS
gulp.task("css", () => {
  del.sync(["./site/static/assets/css/**/*"]);

  const commonPlugins = [
    autoprefixer(),
    postcssPresetEnv(),
    cssnano()
  ];
  
  return merge2(
    gulp.src("./src/css/imports.css")
    .pipe(postcss([cssImport({from: "./src/css/imports.css"})])),
    gulp.src(["./src/scss/imports.scss"])
    .pipe(sass({
      outputStyle:  "nested",
      precision: 10,
      includePaths: ["./node_modules"]
    }).on("error", sass.logError))
  )
  .pipe(gulpif(process.env.NODE_ENV === "development", sourceMaps.init()))
  .pipe(postcss(commonPlugins))
  .pipe(concat("main.css"))
  .pipe(gulpif(process.env.NODE_ENV === "development", sourceMaps.write()))
  .pipe(hash({
    dummyHash: (process.env.NODE_ENV === "development") ? true : false,
    template: "<%= name %>-cache_<%= hash %><%= ext %>"
    }))
  .pipe(gulp.dest("./site/static/assets/css"))
  .pipe(gulpif(process.env.NODE_ENV === "development", browserSync.stream({match: "**/*.css"})))
  .pipe(hash.manifest("./site/data/manifests/css.json", {append: false}))
  .pipe(gulp.dest("."));
});

// Offload all javascript build, minimising, hashing and sourcemap tasks to webpack
gulp.task("js", () => {
  del.sync(["./site/static/assets/js/**/*"]);

  const myConfig = Object.assign({}, webpackConfig);
  const f = filter(["**", "!**/*js.json"], {restore: true, passthrough: false});
  const stream = gulp.src("./src/js/app.js")
    .pipe(gulpWebpack(myConfig, webpack, (err, stats) => {
      if (err) throw new pluginError('webpack', err);
      log(`[webpack] ${stats.toString({
        colors: true,
        progress: true
      })}`);
    }))
    .pipe(f)
    .pipe(gulp.dest("./site/static/assets/js"));

    f.restore.pipe(gulp.dest("./site/data/manifests"));
    return stream;
});

// Move all fonts to a flattened directory
gulp.task("fonts", () => {
  del.sync(["./site/static/assets/font/**/*"]);

  return gulp.src("./src/font/**/*")
    .pipe(flatten())
    .pipe(gulp.dest("./site/static/assets/font"));
});

// Compile hugo files ('nr' variants don't trigger a browserSync reload)
gulp.task("hugo", (cb) => buildSite(cb, hugoArgsStandard));
gulp.task("hugo-nr", (cb) => buildSite(cb, hugoArgsStandard, true));
gulp.task("hugo-preview", (cb) => buildSite(cb, hugoArgsPreview));
gulp.task("hugo-preview-nr", (cb) => buildSite(cb, hugoArgsPreview, true));

// Run hugo and build the site
function buildSite(cb, options, prevent_reload) {
  const args = options ? hugoArgsCommon.concat(options) : hugoArgsCommon;

  del.sync(["./dist/**/*"]);
  del.sync(["./dist-preview/**/*"]);

  spawn(hugo, args, {stdio: "inherit"}).on("close", (code) => {
    if (code === 0) {
      if (browserSync.active && !prevent_reload) browserSync.reload();
      cb();
    } else {
      if (browserSync.active) browserSync.notify("Hugo build failed :(");
      cb("Hugo build failed");
    }
  });
}

// Run development server with browserSync
function runServer(cb, server_mode) {
  browserSync.init({
    server: {
      baseDir: "./dist"
    },
    ghostMode: false,
    open: false
  });

  // Changes here will also, intentionally, result in a hugo rebuild and
  // browserSync.reload (triggered via the watch block further down)
  gulp.watch("./src/js/**/*.js", gulp.series("js"));
  gulp.watch("./src/font/**/*", gulp.series("fonts"));

  // Changes here are streamed live to the browser via browserSync
  gulp.watch([
    "./src/scss/**/*",
    "./src/css/**/*"
    ], gulp.series("css"));

  // Changes here trigger a hugo rebuild and browserSync.reload
  gulp.watch([
    "./site/**/*",
    "!./site/data/manifests/css.json",
    "!./site/static/assets/css/**/*",
    "!./site/static/assets/js/**/*"
    ], gulp.series((server_mode === "server-preview") ? "hugo-preview" : "hugo"));

  // Changes here trigger a hugo rebuild but not a browserSync.reload (sine the
  // css task will have already streamed the changes to the browser)
  gulp.watch("./site/data/manifests/css.json", gulp.series(
    (server_mode === "server-preview") ? "hugo-preview-nr" : "hugo-nr"));

  cb();
};

// Dev entrypoints
gulp.task("server", gulp.series(
    gulp.parallel("css", "js", "fonts"),
    "hugo",
    (cb) => runServer(cb, "server")
  ));

gulp.task("server-preview", gulp.series(
    gulp.parallel("css", "js", "fonts"),
    "hugo-preview",
    (cb) => runServer(cb, "server-preview")
  ));

// Prod entrypoints
gulp.task("build",
  gulp.series(
    gulp.parallel("css", "js", "fonts"),
    "hugo"
  )
);

gulp.task("build-preview",
  gulp.series(
    gulp.parallel("css", "js", "fonts"),
    "hugo-preview"
  )
);
