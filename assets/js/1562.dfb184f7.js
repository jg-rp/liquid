/*! For license information please see 1562.dfb184f7.js.LICENSE.txt */
(()=>{"use strict";__webpack_require__.gca=function(e){return e={}[e]||e,__webpack_require__.p+__webpack_require__.u(e)};const e=Symbol("Comlink.proxy"),t=Symbol("Comlink.endpoint"),n=Symbol("Comlink.releaseProxy"),r=Symbol("Comlink.finalizer"),o=Symbol("Comlink.thrown"),i=e=>"object"==typeof e&&null!==e||"function"==typeof e,a=new Map([["proxy",{canHandle:t=>i(t)&&t[e],serialize(e){const{port1:t,port2:n}=new MessageChannel;return s(e,t),[n,[n]]},deserialize(e){return e.start(),f(e,[],t);var t}}],["throw",{canHandle:e=>i(e)&&o in e,serialize({value:e}){let t;return t=e instanceof Error?{isError:!0,value:{message:e.message,name:e.name,stack:e.stack}}:{isError:!1,value:e},[t,[]]},deserialize(e){if(e.isError)throw Object.assign(new Error(e.value.message),e.value);throw e.value}}]]);function s(t,n=globalThis,i=["*"]){n.addEventListener("message",(function a(c){if(!c||!c.data)return;if(!function(e,t){for(const n of e){if(t===n||"*"===n)return!0;if(n instanceof RegExp&&n.test(t))return!0}return!1}(i,c.origin))return void console.warn(`Invalid origin '${c.origin}' for comlink proxy`);const{id:u,type:p,path:d}=Object.assign({path:[]},c.data),f=(c.data.argumentList||[]).map(_);let y;try{const n=d.slice(0,-1).reduce(((e,t)=>e[t]),t),r=d.reduce(((e,t)=>e[t]),t);switch(p){case"GET":y=r;break;case"SET":n[d.slice(-1)[0]]=_(c.data.value),y=!0;break;case"APPLY":y=r.apply(n,f);break;case"CONSTRUCT":y=function(t){return Object.assign(t,{[e]:!0})}(new r(...f));break;case"ENDPOINT":{const{port1:e,port2:n}=new MessageChannel;s(t,n),y=function(e,t){return m.set(e,t),e}(e,[e])}break;case"RELEASE":y=void 0;break;default:return}}catch(g){y={value:g,[o]:0}}Promise.resolve(y).catch((e=>({value:e,[o]:0}))).then((e=>{const[o,i]=h(e);n.postMessage(Object.assign(Object.assign({},o),{id:u}),i),"RELEASE"===p&&(n.removeEventListener("message",a),l(n),r in t&&"function"==typeof t[r]&&t[r]())})).catch((e=>{const[t,r]=h({value:new TypeError("Unserializable return value"),[o]:0});n.postMessage(Object.assign(Object.assign({},t),{id:u}),r)}))})),n.start&&n.start()}function l(e){(function(e){return"MessagePort"===e.constructor.name})(e)&&e.close()}function c(e){if(e)throw new Error("Proxy has been released and is not useable")}function u(e){return g(e,{type:"RELEASE"}).then((()=>{l(e)}))}const p=new WeakMap,d="FinalizationRegistry"in globalThis&&new FinalizationRegistry((e=>{const t=(p.get(e)||0)-1;p.set(e,t),0===t&&u(e)}));function f(e,r=[],o=function(){}){let i=!1;const a=new Proxy(o,{get(t,o){if(c(i),o===n)return()=>{!function(e){d&&d.unregister(e)}(a),u(e),i=!0};if("then"===o){if(0===r.length)return{then:()=>a};const t=g(e,{type:"GET",path:r.map((e=>e.toString()))}).then(_);return t.then.bind(t)}return f(e,[...r,o])},set(t,n,o){c(i);const[a,s]=h(o);return g(e,{type:"SET",path:[...r,n].map((e=>e.toString())),value:a},s).then(_)},apply(n,o,a){c(i);const s=r[r.length-1];if(s===t)return g(e,{type:"ENDPOINT"}).then(_);if("bind"===s)return f(e,r.slice(0,-1));const[l,u]=y(a);return g(e,{type:"APPLY",path:r.map((e=>e.toString())),argumentList:l},u).then(_)},construct(t,n){c(i);const[o,a]=y(n);return g(e,{type:"CONSTRUCT",path:r.map((e=>e.toString())),argumentList:o},a).then(_)}});return function(e,t){const n=(p.get(t)||0)+1;p.set(t,n),d&&d.register(e,t,e)}(a,e),a}function y(e){const t=e.map(h);return[t.map((e=>e[0])),(n=t.map((e=>e[1])),Array.prototype.concat.apply([],n))];var n}const m=new WeakMap;function h(e){for(const[t,n]of a)if(n.canHandle(e)){const[r,o]=n.serialize(e);return[{type:"HANDLER",name:t,value:r},o]}return[{type:"RAW",value:e},m.get(e)||[]]}function _(e){switch(e.type){case"HANDLER":return a.get(e.name).deserialize(e.value);case"RAW":return e.value}}function g(e,t,n){return new Promise((r=>{const o=new Array(4).fill(0).map((()=>Math.floor(Math.random()*Number.MAX_SAFE_INTEGER).toString(16))).join("-");e.addEventListener("message",(function t(n){n.data&&n.data.id&&n.data.id===o&&(e.removeEventListener("message",t),r(n.data))})),e.start&&e.start(),e.postMessage(Object.assign({id:o},t),n)}))}var b,v=function(e,t,n,r){return new(n||(n=Promise))((function(o,i){function a(e){try{l(r.next(e))}catch(t){i(t)}}function s(e){try{l(r.throw(e))}catch(t){i(t)}}function l(e){var t;e.done?o(e.value):(t=e.value,t instanceof n?t:new n((function(e){e(t)}))).then(a,s)}l((r=r.apply(e,t||[])).next())}))},w=function(e,t){var n,r,o,i,a={label:0,sent:function(){if(1&o[0])throw o[1];return o[1]},trys:[],ops:[]};return i={next:s(0),throw:s(1),return:s(2)},"function"==typeof Symbol&&(i[Symbol.iterator]=function(){return this}),i;function s(s){return function(l){return function(s){if(n)throw new TypeError("Generator is already executing.");for(;i&&(i=0,s[0]&&(a=0)),a;)try{if(n=1,r&&(o=2&s[0]?r.return:s[0]?r.throw||((o=r.return)&&o.call(r),0):r.next)&&!(o=o.call(r,s[1])).done)return o;switch(r=0,o&&(s=[2&s[0],o.value]),s[0]){case 0:case 1:o=s;break;case 4:return a.label++,{value:s[1],done:!1};case 5:a.label++,r=s[1],s=[0];continue;case 7:s=a.ops.pop(),a.trys.pop();continue;default:if(!(o=a.trys,(o=o.length>0&&o[o.length-1])||6!==s[0]&&2!==s[0])){a=0;continue}if(3===s[0]&&(!o||s[1]>o[0]&&s[1]<o[3])){a.label=s[1];break}if(6===s[0]&&a.label<o[1]){a.label=o[1],o=s;break}if(o&&a.label<o[2]){a.label=o[2],a.ops.push(s);break}o[2]&&a.ops.pop(),a.trys.pop();continue}s=t.call(e,a)}catch(l){s=[6,l],r=0}finally{n=o=0}if(5&s[0])throw s[1];return{value:s[0]?s[1]:void 0,done:!0}}([s,l])}}},E=function(e){var t="function"==typeof Symbol&&Symbol.iterator,n=t&&e[t],r=0;if(n)return n.call(e);if(e&&"number"==typeof e.length)return{next:function(){return e&&r>=e.length&&(e=void 0),{value:e&&e[r++],done:!e}}};throw new TypeError(t?"Object is not iterable.":"Symbol.iterator is not defined.")},S=function(e,t){var n="function"==typeof Symbol&&e[Symbol.iterator];if(!n)return e;var r,o,i=n.call(e),a=[];try{for(;(void 0===t||t-- >0)&&!(r=i.next()).done;)a.push(r.value)}catch(s){o={error:s}}finally{try{r&&!r.done&&(n=i.return)&&n.call(i)}finally{if(o)throw o.error}}return a};importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js"),"localhost"!==self.location.hostname&&(console.log=function(){},console.error=function(){});var k={getInput:function(e,t){var n=new XMLHttpRequest;return n.open("GET","/react-py-get-input/?id=".concat(e,"&prompt=").concat(t),!1),n.send(null),n.responseText}};s({init:function(e,t,n){return v(this,void 0,void 0,(function(){var r,o,i,a,s,l,c,u,p,d;return w(this,(function(f){switch(f.label){case 0:return r=self,[4,self.loadPyodide({})];case 1:return r.pyodide=f.sent(),[4,self.pyodide.loadPackage(["pyodide-http"])];case 2:return f.sent(),n[0].length>0?[4,self.pyodide.loadPackage(n[0])]:[3,4];case 3:f.sent(),f.label=4;case 4:return n[1].length>0?[4,self.pyodide.loadPackage(["micropip"])]:[3,7];case 5:return f.sent(),[4,self.pyodide.pyimport("micropip").install(n[1])];case 6:f.sent(),f.label=7;case 7:return o=self.crypto.randomUUID(),i=self.pyodide.version,self.pyodide.registerJsModule("react_py",k),a=self.pyodide.globals.get("dict")(),'\nimport pyodide_http\npyodide_http.patch_all()\n\nimport sys\nfrom pyodide.ffi import to_js\nfrom pyodide.console import PyodideConsole, repr_shorten, BANNER\nimport __main__\nBANNER = "Welcome to the Pyodide terminal emulator \ud83d\udc0d\\n" + BANNER\npyconsole = PyodideConsole(__main__.__dict__)\nimport builtins\nasync def await_fut(fut):\n  res = await fut\n  if res is not None:\n    builtins._ = res\n  return to_js([res], depth=1)\ndef clear_console():\n  pyconsole.buffer = []\n',[4,self.pyodide.runPythonAsync('\nimport pyodide_http\npyodide_http.patch_all()\n\nimport sys\nfrom pyodide.ffi import to_js\nfrom pyodide.console import PyodideConsole, repr_shorten, BANNER\nimport __main__\nBANNER = "Welcome to the Pyodide terminal emulator \ud83d\udc0d\\n" + BANNER\npyconsole = PyodideConsole(__main__.__dict__)\nimport builtins\nasync def await_fut(fut):\n  res = await fut\n  if res is not None:\n    builtins._ = res\n  return to_js([res], depth=1)\ndef clear_console():\n  pyconsole.buffer = []\n',{globals:a})];case 8:return f.sent(),s='\nimport sys, builtins\nimport react_py\n__prompt_str__ = ""\ndef get_input(prompt=""):\n    global __prompt_str__\n    __prompt_str__ = prompt\n    print(prompt, end="")\n    s = react_py.getInput("'.concat(o,'", prompt)\n    print()\n    return s\nbuiltins.input = get_input\nsys.stdin.readline = lambda: react_py.getInput("').concat(o,'", __prompt_str__)\n'),[4,self.pyodide.runPythonAsync(s,{globals:a})];case 9:return f.sent(),l=a.get("repr_shorten"),c=a.get("BANNER"),u=a.get("await_fut"),p=a.get("pyconsole"),d=a.get("clear_console"),a.destroy(),p.stdout_callback=e,b={reprShorten:l,awaitFut:u,pyconsole:p,clearConsole:d},t({id:o,version:i,banner:c}),[2]}}))}))},run:function(e){return v(this,void 0,void 0,(function(){var t,n,r,o,i,a,s,l,c,u,p,d,f;return w(this,(function(y){switch(y.label){case 0:if(!b)throw new Error("Console has not been initialised");if(void 0===e)throw new Error("No code to push");y.label=1;case 1:y.trys.push([1,9,10,11]),n=E(e.split("\n")),r=n.next(),y.label=2;case 2:if(r.done)return[3,8];o=r.value,i=b.pyconsole.push(o),t=i.syntax_check,a=b.awaitFut(i),y.label=3;case 3:return y.trys.push([3,5,6,7]),[4,a];case 4:return s=S.apply(void 0,[y.sent(),1]),l=s[0],self.pyodide.isPyProxy(l)&&l.destroy(),[3,7];case 5:if("PythonError"===(c=y.sent()).constructor.name)return u=i.formatted_error||c.message,[2,{state:t,error:u.trimEnd()}];throw c;case 6:return i.destroy(),a.destroy(),[7];case 7:return r=n.next(),[3,2];case 8:return[3,11];case 9:return p=y.sent(),d={error:p},[3,11];case 10:try{r&&!r.done&&(f=n.return)&&f.call(n)}finally{if(d)throw d.error}return[7];case 11:return[2,{state:t}]}}))}))},readFile:function(e){return self.pyodide.FS.readFile(e,{encoding:"utf8"})},writeFile:function(e,t){return self.pyodide.FS.writeFile(e,t,{encoding:"utf8"})},mkdir:function(e){self.pyodide.FS.mkdir(e)},rmdir:function(e){self.pyodide.FS.rmdir(e)}})})();