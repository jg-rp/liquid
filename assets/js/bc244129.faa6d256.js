"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[8173],{3564:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>p,contentTitle:()=>o,default:()=>d,frontMatter:()=>i,metadata:()=>l,toc:()=>s});var a=n(3117),r=(n(7294),n(3905));const i={},o="JSONPath Filters",l={unversionedId:"jsonpath/filters",id:"jsonpath/filters",title:"JSONPath Filters",description:"This page documents filters included with the Liquid JSONPath package. See the filter reference for details of all standard filters. Also see the Python JSONPath docs for JSONPath selector syntax.",source:"@site/docs/jsonpath/filters.md",sourceDirName:"jsonpath",slug:"/jsonpath/filters",permalink:"/liquid/jsonpath/filters",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/jsonpath/filters.md",tags:[],version:"current",frontMatter:{},sidebar:"languageSidebar",previous:{title:"Python Liquid JSONPath",permalink:"/liquid/jsonpath/introduction"},next:{title:"JSONPath Tags",permalink:"/liquid/jsonpath/tags"}},p={},s=[{value:"find",id:"find",level:2},{value:"Options",id:"options",level:3},{value:"Customizing JSONPath",id:"customizing-jsonpath",level:3}],u={toc:s};function d(e){let{components:t,...n}=e;return(0,r.kt)("wrapper",(0,a.Z)({},u,n,{components:t,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"jsonpath-filters"},"JSONPath Filters"),(0,r.kt)("p",null,"This page documents filters included with the ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/jg-rp/liquid-jsonpath"},"Liquid JSONPath")," package. See the ",(0,r.kt)("a",{parentName:"p",href:"/liquid/language/filters"},"filter reference")," for details of all standard filters. Also see the ",(0,r.kt)("a",{parentName:"p",href:"https://jg-rp.github.io/python-jsonpath/syntax/"},"Python JSONPath docs")," for JSONPath selector syntax."),(0,r.kt)("h2",{id:"find"},"find"),(0,r.kt)("p",null,(0,r.kt)("inlineCode",{parentName:"p"},"<object> | find: <string> -> <list>")),(0,r.kt)("p",null,"Return the result of applying a ",(0,r.kt)("em",{parentName:"p"},"jsonpath string")," to the input value. The input value should be a list (or any sequence) or a dict (or any mapping)."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-liquid"},"{{ site | find: '$.users.*.name' | join: ' ' }}\n")),(0,r.kt)("p",null,"If the following data was assigned to a variable called ",(0,r.kt)("inlineCode",{parentName:"p"},"site"),":"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-json",metastring:'title="data"',title:'"data"'},'{\n  "users": [\n    {\n      "name": "Sue",\n      "score": 100\n    },\n    {\n      "name": "John",\n      "score": 86\n    },\n    {\n      "name": "Sally",\n      "score": 84\n    },\n    {\n      "name": "Jane",\n      "score": 55\n    }\n  ]\n}\n')),(0,r.kt)("p",null,"We'd get an output like this:"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"Sue John Sally Jane\n")),(0,r.kt)("h3",{id:"options"},"Options"),(0,r.kt)("p",null,"The ",(0,r.kt)("inlineCode",{parentName:"p"},"find")," filter defaults to returning an ",(0,r.kt)("a",{parentName:"p",href:"/liquid/guides/undefined-variables"},"undefined")," instance when given anything other than a mapping or sequence as its input value. You can change this behavior by setting the ",(0,r.kt)("inlineCode",{parentName:"p"},"default")," argument to one of ",(0,r.kt)("inlineCode",{parentName:"p"},"Default.EMPTY"),", ",(0,r.kt)("inlineCode",{parentName:"p"},"Default.RAISE")," or ",(0,r.kt)("inlineCode",{parentName:"p"},"Default.UNDEFINED")," when registering ",(0,r.kt)("inlineCode",{parentName:"p"},"find")," with an environment."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid_jsonpath import Default\nfrom liquid_jsonpath import Find\n\nenv = Environment()\nenv.add_filter("find", Find(default=Default.RAISE))\n# ...\n')),(0,r.kt)("p",null,(0,r.kt)("inlineCode",{parentName:"p"},"Default.RAISE")," will raise a ",(0,r.kt)("inlineCode",{parentName:"p"},"FilterArgumentError")," when given an unacceptable input value or JSONPath string, and ",(0,r.kt)("inlineCode",{parentName:"p"},"Default.EMPTY")," will simply return an empty list instead."),(0,r.kt)("h3",{id:"customizing-jsonpath"},"Customizing JSONPath"),(0,r.kt)("p",null,"The ",(0,r.kt)("inlineCode",{parentName:"p"},"find")," filter uses a ",(0,r.kt)("a",{parentName:"p",href:"https://jg-rp.github.io/python-jsonpath/api/#jsonpath.JSONPathEnvironment"},(0,r.kt)("inlineCode",{parentName:"a"},"JSONPathEnvironment"))," with its default configuration. You can replace the ",(0,r.kt)("inlineCode",{parentName:"p"},"JSONPathEnvironment")," used by ",(0,r.kt)("inlineCode",{parentName:"p"},"find")," by subclassing ",(0,r.kt)("inlineCode",{parentName:"p"},"liquid_jsonpath.Find")," and setting the ",(0,r.kt)("inlineCode",{parentName:"p"},"jsonpath_class")," class attribute."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'from jsonpath import JSONPathEnvironment\nfrom liquid_jsonpath import Find\n\nclass MyJSONPathEnv(JSONPathEnvironment):\n    root_token = "^"  # silly example\n\nclass MyFindFilter(Find):\n    jsonpath_class = MyJSONPathEnv\n\nenv = Environment()\nenv.add_filter("find", MyFindFilter())\n')))}d.isMDXComponent=!0},3905:(e,t,n)=>{n.d(t,{Zo:()=>u,kt:()=>h});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},i=Object.keys(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(a=0;a<i.length;a++)n=i[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var p=a.createContext({}),s=function(e){var t=a.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},u=function(e){var t=s(e.components);return a.createElement(p.Provider,{value:t},e.children)},d={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},c=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,i=e.originalType,p=e.parentName,u=l(e,["components","mdxType","originalType","parentName"]),c=s(n),h=r,f=c["".concat(p,".").concat(h)]||c[h]||d[h]||i;return n?a.createElement(f,o(o({ref:t},u),{},{components:n})):a.createElement(f,o({ref:t},u))}));function h(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var i=n.length,o=new Array(i);o[0]=c;var l={};for(var p in t)hasOwnProperty.call(t,p)&&(l[p]=t[p]);l.originalType=e,l.mdxType="string"==typeof e?e:r,o[1]=l;for(var s=2;s<i;s++)o[s]=n[s];return a.createElement.apply(null,o)}return a.createElement.apply(null,n)}c.displayName="MDXCreateElement"}}]);