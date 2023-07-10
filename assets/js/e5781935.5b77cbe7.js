"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4726],{3905:(e,t,n)=>{n.d(t,{Zo:()=>c,kt:()=>f});var r=n(7294);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function p(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},o=Object.keys(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(r=0;r<o.length;r++)n=o[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var l=r.createContext({}),u=function(e){var t=r.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},c=function(e){var t=u(e.components);return r.createElement(l.Provider,{value:t},e.children)},s="mdxType",m={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,o=e.originalType,l=e.parentName,c=p(e,["components","mdxType","originalType","parentName"]),s=u(n),d=a,f=s["".concat(l,".").concat(d)]||s[d]||m[d]||o;return n?r.createElement(f,i(i({ref:t},c),{},{components:n})):r.createElement(f,i({ref:t},c))}));function f(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var o=n.length,i=new Array(o);i[0]=d;var p={};for(var l in t)hasOwnProperty.call(t,l)&&(p[l]=t[l]);p.originalType=e,p[s]="string"==typeof e?e:a,i[1]=p;for(var u=2;u<o;u++)i[u]=n[u];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},2872:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>l,contentTitle:()=>i,default:()=>m,frontMatter:()=>o,metadata:()=>p,toc:()=>u});var r=n(7462),a=(n(7294),n(3905));const o={},i="HTML Auto-Escape",p={unversionedId:"introduction/auto-escape",id:"introduction/auto-escape",title:"HTML Auto-Escape",description:"Python Liquid offers HTML auto-escaping. Where render context variables are automatically escaped on output. Install optional dependencies for auto-escaping using the autoescape extra.",source:"@site/docs/introduction/auto-escape.md",sourceDirName:"introduction",slug:"/introduction/auto-escape",permalink:"/liquid/introduction/auto-escape",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/introduction/auto-escape.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Comments",permalink:"/liquid/introduction/comments"},next:{title:"Async Support",permalink:"/liquid/introduction/async-support"}},l={},u=[{value:"Markup",id:"markup",level:2},{value:"Safe",id:"safe",level:2}],c={toc:u},s="wrapper";function m(e){let{components:t,...n}=e;return(0,a.kt)(s,(0,r.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"html-auto-escape"},"HTML Auto-Escape"),(0,a.kt)("p",null,"Python Liquid offers HTML auto-escaping. Where render context variables are automatically escaped on output. Install optional dependencies for auto-escaping using the ",(0,a.kt)("inlineCode",{parentName:"p"},"autoescape")," extra."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-shell"},"$ pipenv install python-liquid[autoescape]\n")),(0,a.kt)("p",null,"Or"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-shell"},"$ python -m pip install -U python-liquid[autoescape]\n")),(0,a.kt)("p",null,"Auto-escaping is disabled by default. Enable it by setting the ",(0,a.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,a.kt)("inlineCode",{parentName:"a"},"Environment"))," or ",(0,a.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,a.kt)("inlineCode",{parentName:"a"},"Template"))," ",(0,a.kt)("inlineCode",{parentName:"p"},"autoescape")," argument to ",(0,a.kt)("inlineCode",{parentName:"p"},"True"),"."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nenv = Environment(autoescape=True)\ntemplate = env.from_string("<p>Hello, {{ you }}</p>")\nprint(template.render(you=\'</p><script>alert("XSS!");<\/script>\'))\n')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"<p>Hello, &lt;/p&gt;&lt;script&gt;alert(&#34;XSS!&#34;);&lt;/script&gt;</p>\n")),(0,a.kt)("h2",{id:"markup"},"Markup"),(0,a.kt)("p",null,'Mark a string as "safe" by wrapping it in a ',(0,a.kt)("inlineCode",{parentName:"p"},"Markup")," object."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment, Markup\nenv = Environment(autoescape=True)\ntemplate = env.from_string("<p>Hello, {{ you }}</p>")\nprint(template.render(you=Markup("<em>World!</em>")))\n')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain",metastring:"title=output",title:"output"},"'<p>Hello, <em>World!</em></p>'\n")),(0,a.kt)("h2",{id:"safe"},"Safe"),(0,a.kt)("p",null,"Alternatively use the non-standard ",(0,a.kt)("a",{parentName:"p",href:"/liquid/language/filters#safe"},"safe")," filter."),(0,a.kt)("admonition",{type:"caution"},(0,a.kt)("p",{parentName:"admonition"},"The ",(0,a.kt)("inlineCode",{parentName:"p"},"safe"),' filter is not available in "standard" Liquid.')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nenv = Environment(autoescape=True)\ntemplate = env.from_string("<p>Hello, {{ you | safe }}</p>")\nprint(template.render(you="<em>World!</em>"))\n')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain",metastring:"title=output",title:"output"},"'<p>Hello, <em>World!</em></p>'\n")))}m.isMDXComponent=!0}}]);