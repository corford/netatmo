/* Polyfills */
// NodeList.prototype.forEach() iteration (taken from MDN example)
if (window.NodeList && !NodeList.prototype.forEach) {
	NodeList.prototype.forEach = function (callback, thisArg) {
		thisArg = thisArg || window;
		for (var i = 0; i < this.length; i++) {
			callback.call(thisArg, this[i], i, this);
		}
	};
}

// Some polyfills assume URLSearchParams but IE11 doesn't natively support it,
// so we add it as a global here
import URLSearchParams from '@ungap/url-search-params';
global.URLSearchParams = URLSearchParams;

import '@babel/polyfill';
import 'whatwg-fetch';
import 'intersection-observer';
import 'custom-event-polyfill';

/* App code starts here */
import activateSandbox from './sandbox';

document.addEventListener('DOMContentLoaded', () => {
  activateSandbox();
});


window.addEventListener('load', () => {
  // Attach any global events here that need to wait until all page
  // content (images etc.) is fully loaded and rendered
});
