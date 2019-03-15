import webpack from "webpack";
import UglifyJsPlugin from "uglifyjs-webpack-plugin";
import ManifestPlugin from "webpack-manifest-plugin";
import path from "path";

const isProd = process.env.NODE_ENV !== 'development';
const ifProd = x => isProd && x;
const ifDev = x => !isProd && x;

export default {
  mode: isProd ? 'production' : 'development',
  devtool: 'source-map',
  bail: true,

  module: {
    rules: [
      {
        test: /\.json$/,
        use: ['json-loader']
      },
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: [{
          loader: 'babel-loader',
          options: {
            cacheDirectory: true
          }
        }]
      }
    ]
  },

  optimization: {
    concatenateModules: true,
    runtimeChunk: 'single',
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'all'
        }
      }
    },    
    minimize: true,
    minimizer: [
      new UglifyJsPlugin({
        test: /\.js$/,
        cache: false,
        sourceMap: true,
        uglifyOptions: {
          output: {
            comments: false
          }
        }
      })
    ]
  },

  plugins: [
    new webpack.EnvironmentPlugin({
      NODE_ENV: 'production', // use 'production' unless process.env.NODE_ENV is defined
      DEBUG: false
    }),

    new webpack.LoaderOptionsPlugin({
      debug: (process.env.DEBUG === 'true') ? true : false
    }),

    new webpack.HashedModuleIdsPlugin(),

    new ManifestPlugin({
      fileName: 'js.json',
      publicPath: ''
    })  
  ],

  context: path.join(__dirname, 'src'),
  entry: {
    app: ['./js/app']
  },
  output: {
    path: path.join(__dirname, 'site/static/assets/js'),
    publicPath: '',
    filename: isProd ? '[name]-cache_[contenthash:8].js' : '[name]-cache_00000000.js', // we want deterministic filenames in dev mode
    sourceMapFilename: '__src.[name].js.map'
  },
  watch: false
};
