"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[7029],{3905:(e,n,t)=>{t.d(n,{Zo:()=>u,kt:()=>m});var i=t(7294);function r(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function a(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);n&&(i=i.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,i)}return t}function l(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?a(Object(t),!0).forEach((function(n){r(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):a(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function d(e,n){if(null==e)return{};var t,i,r=function(e,n){if(null==e)return{};var t,i,r={},a=Object.keys(e);for(i=0;i<a.length;i++)t=a[i],n.indexOf(t)>=0||(r[t]=e[t]);return r}(e,n);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(i=0;i<a.length;i++)t=a[i],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(r[t]=e[t])}return r}var o=i.createContext({}),s=function(e){var n=i.useContext(o),t=n;return e&&(t="function"==typeof e?e(n):l(l({},n),e)),t},u=function(e){var n=s(e.components);return i.createElement(o.Provider,{value:n},e.children)},p="mdxType",f={inlineCode:"code",wrapper:function(e){var n=e.children;return i.createElement(i.Fragment,{},n)}},c=i.forwardRef((function(e,n){var t=e.components,r=e.mdxType,a=e.originalType,o=e.parentName,u=d(e,["components","mdxType","originalType","parentName"]),p=s(t),c=r,m=p["".concat(o,".").concat(c)]||p[c]||f[c]||a;return t?i.createElement(m,l(l({ref:n},u),{},{components:t})):i.createElement(m,l({ref:n},u))}));function m(e,n){var t=arguments,r=n&&n.mdxType;if("string"==typeof e||r){var a=t.length,l=new Array(a);l[0]=c;var d={};for(var o in n)hasOwnProperty.call(n,o)&&(d[o]=n[o]);d.originalType=e,d[p]="string"==typeof e?e:r,l[1]=d;for(var s=2;s<a;s++)l[s]=t[s];return i.createElement.apply(null,l)}return i.createElement.apply(null,t)}c.displayName="MDXCreateElement"},299:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>o,contentTitle:()=>l,default:()=>f,frontMatter:()=>a,metadata:()=>d,toc:()=>s});var i=t(7462),r=(t(7294),t(3905));const a={},l="Undefined Variables",d={unversionedId:"guides/undefined-variables",id:"guides/undefined-variables",title:"Undefined Variables",description:'When rendering a Liquid template, if a variable name can not be resolved, an instance of liquid.Undefined is used instead. We can customize template rendering behavior by implementing some of Python\'s "magic" methods on a subclass of liquid.Undefined.',source:"@site/docs/guides/undefined-variables.md",sourceDirName:"guides",slug:"/guides/undefined-variables",permalink:"/liquid/guides/undefined-variables",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/guides/undefined-variables.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Tag Analysis",permalink:"/liquid/guides/tag-analysis"},next:{title:"Whitespace Suppression",permalink:"/liquid/guides/whitespace-suppression"}},o={},s=[{value:"Default Undefined",id:"default-undefined",level:2},{value:"Strict Undefined",id:"strict-undefined",level:2},{value:"The default filter",id:"the-default-filter",level:2},{value:"Falsy StrictUndefined",id:"falsy-strictundefined",level:2}],u={toc:s},p="wrapper";function f(e){let{components:n,...t}=e;return(0,r.kt)(p,(0,i.Z)({},u,t,{components:n,mdxType:"MDXLayout"}),(0,r.kt)("h1",{id:"undefined-variables"},"Undefined Variables"),(0,r.kt)("p",null,"When rendering a Liquid template, if a variable name can not be resolved, an instance of ",(0,r.kt)("inlineCode",{parentName:"p"},"liquid.Undefined")," is used instead. We can customize template rendering behavior by implementing some of ",(0,r.kt)("a",{parentName:"p",href:"https://docs.python.org/3/reference/datamodel.html#basic-customization"},'Python\'s "magic" methods')," on a subclass of ",(0,r.kt)("inlineCode",{parentName:"p"},"liquid.Undefined"),"."),(0,r.kt)("h2",{id:"default-undefined"},"Default Undefined"),(0,r.kt)("p",null,"All operations on the default ",(0,r.kt)("inlineCode",{parentName:"p"},"Undefined")," type are silently ignored and, when rendered, it produces an empty string. For example, you can access properties and iterate an undefined variable without error."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"Hello {{ nosuchthing }}\n{% for thing in nosuchthing %}\n    {{ thing }}\n{% endfor %}\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"Hello\n\n\n\n")),(0,r.kt)("h2",{id:"strict-undefined"},"Strict Undefined"),(0,r.kt)("p",null,"When ",(0,r.kt)("inlineCode",{parentName:"p"},"liquid.StrictUndefined")," is passed as the ",(0,r.kt)("inlineCode",{parentName:"p"},"undefined")," argument to ",(0,r.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,r.kt)("inlineCode",{parentName:"a"},"Environment"))," or ",(0,r.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,r.kt)("inlineCode",{parentName:"a"},"Template")),", any operation on an undefined variable will raise an ",(0,r.kt)("inlineCode",{parentName:"p"},"UndefinedError"),"."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"from liquid import Environment, StrictUndefined\n\nenv = Environment(undefined=StrictUndefined)\ntemplate = env.from_string(\"Hello {{ nosuchthing }}\")\ntemplate.render()\n# UndefinedError: 'nosuchthing' is undefined, on line 1\n")),(0,r.kt)("h2",{id:"the-default-filter"},"The default filter"),(0,r.kt)("p",null,"With ",(0,r.kt)("inlineCode",{parentName:"p"},"StrictUndefined"),", the built-in ",(0,r.kt)("a",{parentName:"p",href:"/liquid/language/filters#default"},(0,r.kt)("inlineCode",{parentName:"a"},"default"))," filter does not handle undefined variables the ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/Shopify/liquid/issues/1404"},"way you might expect"),". The following example will raise an ",(0,r.kt)("inlineCode",{parentName:"p"},"UndefinedError")," if ",(0,r.kt)("inlineCode",{parentName:"p"},"username")," is undefined."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-liquid"},'Hello {{ username | default: "user" }}\n')),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},(0,r.kt)("em",{parentName:"strong"},"New in version 1.4.0"))),(0,r.kt)("p",null,"We can use the built-in ",(0,r.kt)("inlineCode",{parentName:"p"},"StrictDefaultUndefined")," type, which plays nicely with the ",(0,r.kt)("inlineCode",{parentName:"p"},"default")," filter, while still providing strictness elsewhere."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},"from liquid import Environment\nfrom liquid import StrictDefaultUndefined\n\nenv = Environment(undefined=StrictDefaultUndefined)\ntemplate = env.from_string('Hello {{ username | default: \"user\" }}')\nprint(template.render())\n")),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"Hello user\n")),(0,r.kt)("h2",{id:"falsy-strictundefined"},"Falsy StrictUndefined"),(0,r.kt)("p",null,"It's usually ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/Shopify/liquid/issues/1034"},"not possible")," to detect undefined variables in a template using an ",(0,r.kt)("a",{parentName:"p",href:"../language/tags#if"},(0,r.kt)("inlineCode",{parentName:"a"},"if"))," tag. In Python Liquid we can implement an ",(0,r.kt)("inlineCode",{parentName:"p"},"Undefined")," type that allows us to write ",(0,r.kt)("inlineCode",{parentName:"p"},"{% if nosuchthing %}"),", but still get some strictness when undefined variables are used elsewhere."),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid import StrictUndefined\n\nclass FalsyStrictUndefined(StrictUndefined):\n    def __bool__(self) -> bool:\n        return False\n\n    def __eq__(self, other: object) -> bool:\n        if other is False:\n            return True\n        raise UndefinedError(self.msg)\n\nenv = Environment(undefined=FalsyStrictUndefined)\n\ntemplate = env.from_string("{% if nosuchthing %}foo{% else %}bar{% endif %}")\ntemplate.render() # "bar"\n\ntemplate = env.from_string("{{ nosuchthing }}")\ntemplate.render()\n# UndefinedError: \'nosuchthing\' is undefined, on line 1\n')))}f.isMDXComponent=!0}}]);