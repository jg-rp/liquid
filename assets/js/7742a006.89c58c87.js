"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[8870],{3226:(e,t,n)=>{n.r(t),n.d(t,{contentTitle:()=>o,default:()=>u,frontMatter:()=>r,metadata:()=>l,toc:()=>s});var i=n(3117),a=(n(7294),n(3905));const r={title:"Compatibility",description:"Known incompatibilities between Python Liquid and Ruby Liquid",hide_table_of_contents:!1},o="Known Issues",l={type:"mdx",permalink:"/liquid/known_issues",source:"@site/src/pages/known_issues.md",title:"Compatibility",description:"Known incompatibilities between Python Liquid and Ruby Liquid",frontMatter:{title:"Compatibility",description:"Known incompatibilities between Python Liquid and Ruby Liquid",hide_table_of_contents:!1}},s=[{value:"Coercing Strings to Integers Inside Filters",id:"coercing-strings-to-integers-inside-filters",level:2},{value:"Comment Parsing",id:"comment-parsing",level:2},{value:"Counters",id:"counters",level:2},{value:"Cycle Arguments",id:"cycle-arguments",level:2},{value:"Cycle Groups",id:"cycle-groups",level:2},{value:"The Date Filter",id:"the-date-filter",level:2},{value:"Error Handling",id:"error-handling",level:2},{value:"Floats in Ranges",id:"floats-in-ranges",level:2},{value:"Indexable Strings",id:"indexable-strings",level:2}],p={toc:s};function u(e){let{components:t,...n}=e;return(0,a.kt)("wrapper",(0,i.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"known-issues"},"Known Issues"),(0,a.kt)("p",null,"This page documents known compatibility issues between Python Liquid's default ",(0,a.kt)("a",{parentName:"p",href:"/api/Environment"},(0,a.kt)("inlineCode",{parentName:"a"},"Environment"))," and the ",(0,a.kt)("a",{parentName:"p",href:"https://shopify.github.io/liquid/"},"reference implementation")," of Liquid, written in Ruby. We strive to be 100% compatible with the reference implementation. That is, given an equivalent render context, a template rendered with Python Liquid should produce the same output as when rendered with Ruby Liquid."),(0,a.kt)("admonition",{type:"info"},(0,a.kt)("p",{parentName:"admonition"},"Python Liquid version 1.7.0 introduced ",(0,a.kt)("a",{parentName:"p",href:"/api/future-environment"},(0,a.kt)("inlineCode",{parentName:"a"},"liquid.future.Environment"))," as an alternative to the default ",(0,a.kt)("a",{parentName:"p",href:"/api/Environment"},(0,a.kt)("inlineCode",{parentName:"a"},"Environment")),". This alternative environment is intended to transition Python Liquid towards greater compatibility with Ruby Liquid, without changing template rendering behavior for existing Python Liquid users."),(0,a.kt)("p",{parentName:"admonition"},"Some of the issues described below have been resolved with ",(0,a.kt)("inlineCode",{parentName:"p"},"liquid.future.Environment"),". To use it, simply import ",(0,a.kt)("inlineCode",{parentName:"p"},"Environment")," from ",(0,a.kt)("inlineCode",{parentName:"p"},"liquid.future")," instead if ",(0,a.kt)("inlineCode",{parentName:"p"},"liquid"),".")),(0,a.kt)("h2",{id:"coercing-strings-to-integers-inside-filters"},"Coercing Strings to Integers Inside Filters"),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},(0,a.kt)("em",{parentName:"strong"},"See issue ",(0,a.kt)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/49"},"#49")))),(0,a.kt)("p",null,"Many filters built in to Liquid will automatically convert a string representation of a number to an integer or float as needed. When converting integers, Ruby Liquid uses ",(0,a.kt)("a",{parentName:"p",href:"https://ruby-doc.org/core-3.1.1/String.html#method-i-to_i"},"Ruby's String.to_i method"),", which will disregard trailing non-digit characters. In the following example, ",(0,a.kt)("inlineCode",{parentName:"p"},"'7,42'")," is converted to ",(0,a.kt)("inlineCode",{parentName:"p"},"7")),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"template:")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-liquid"},"{{ 3.14 | plus: '7,42' }}\n{{ '123abcdef45' | plus: '1,,,,..!@qwerty' }}\n")),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"output")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain"},"10.14\n124\n")),(0,a.kt)("p",null,"Python Liquid currently falls back to ",(0,a.kt)("inlineCode",{parentName:"p"},"0")," for any string that can't be converted to an integer in its entirety. As is the case in Ruby Liquid for strings without leading digits."),(0,a.kt)("p",null,"This does not apply to parsing of integer literals, only converting strings to integers (not floats) inside filters."),(0,a.kt)("h2",{id:"comment-parsing"},"Comment Parsing"),(0,a.kt)("p",null,"Python Liquid will raise a ",(0,a.kt)("inlineCode",{parentName:"p"},"LiquidSyntaxError")," if it finds the string ",(0,a.kt)("inlineCode",{parentName:"p"},"{% endcomment %}")," inside a comment block. Ruby Liquid, on the other hand, will successfully parse fully-formed nested comment blocks, but will fail to parse a comment block containing either a ",(0,a.kt)("inlineCode",{parentName:"p"},"{% comment %}")," or ",(0,a.kt)("inlineCode",{parentName:"p"},"{% endcomment %}")," on its own."),(0,a.kt)("h2",{id:"counters"},"Counters"),(0,a.kt)("p",null,"In Ruby Liquid, the built-in ",(0,a.kt)("a",{parentName:"p",href:"/language/tags#increment"},(0,a.kt)("inlineCode",{parentName:"a"},"increment"))," and ",(0,a.kt)("a",{parentName:"p",href:"/language/tags#decrement"},(0,a.kt)("inlineCode",{parentName:"a"},"decrement")),' tags can, in some cases, mutate "global" context and keep named counters alive between renders. Although not difficult to implement, I can\'t quite bring myself to do it.'),(0,a.kt)("h2",{id:"cycle-arguments"},"Cycle Arguments"),(0,a.kt)("p",null,"Python Liquid will accept ",(0,a.kt)("a",{parentName:"p",href:"/language/tags#cycle"},(0,a.kt)("inlineCode",{parentName:"a"},"cycle")),' arguments of any type, including identifiers to be resolved, this behavior is considered "unintended" or "undefined" in Ruby Liquid (see ',(0,a.kt)("a",{parentName:"p",href:"https://github.com/Shopify/liquid/issues/1519"},"issue #1519"),"). If you need interoperability between Python Liquid and Ruby Liquid, only use strings or numbers as arguments to ",(0,a.kt)("inlineCode",{parentName:"p"},"cycle"),"."),(0,a.kt)("h2",{id:"cycle-groups"},"Cycle Groups"),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},(0,a.kt)("em",{parentName:"strong"},"See issue ",(0,a.kt)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/43"},"#43")))),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},(0,a.kt)("em",{parentName:"strong"},"Fixed in version 1.7.0"))," with ",(0,a.kt)("a",{parentName:"p",href:"/api/future-environment"},(0,a.kt)("inlineCode",{parentName:"a"},"liquid.future.Environment")),"."),(0,a.kt)("p",null,"When the ",(0,a.kt)("a",{parentName:"p",href:"/language/tags#cycle"},(0,a.kt)("inlineCode",{parentName:"a"},"cycle"))," tag is given a name, Python Liquid will use that name and all other arguments to distinguish one cycle from another. Ruby Liquid will disregard all other arguments when given a name. For example."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-liquid"},'{% cycle a: 1, 2, 3 %}\n{% cycle a: "x", "y", "z" %}\n{% cycle a: 1, 2, 3 %}\n')),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Ruby Liquid Output:")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain"},"1\ny\n3\n")),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Python Liquid Output:")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain"},"1\nx\n2\n")),(0,a.kt)("h2",{id:"the-date-filter"},"The Date Filter"),(0,a.kt)("p",null,"The built-in ",(0,a.kt)("a",{parentName:"p",href:"/language/filters#date"},(0,a.kt)("inlineCode",{parentName:"a"},"date"))," filter uses ",(0,a.kt)("a",{parentName:"p",href:"https://dateutil.readthedocs.io/en/stable/"},"dateutil")," for parsing strings to ",(0,a.kt)("inlineCode",{parentName:"p"},"datetime"),"s, and ",(0,a.kt)("inlineCode",{parentName:"p"},"strftime")," for formatting. There are likely to be some inconsistencies between this and the reference implementation's equivalent parsing and formatting of dates and times."),(0,a.kt)("h2",{id:"error-handling"},"Error Handling"),(0,a.kt)("p",null,"Python Liquid might not handle syntax or type errors in the same way as the reference implementation. We might fail earlier or later, and will almost certainly produce a different error message."),(0,a.kt)("p",null,'Python Liquid does not have a "lax" parser, like Ruby Liquid. Upon finding an error, Python Liquid\'s ',(0,a.kt)("a",{parentName:"p",href:"/introduction/strictness"},"lax mode")," simply discards the current block and continues to parse/render the next block, if one is available. Also, Python Liquid will never inject error messages into an output document. Although this can be achieved by extending ",(0,a.kt)("a",{parentName:"p",href:"/api/BoundTemplate"},(0,a.kt)("inlineCode",{parentName:"a"},"BoundTemplate"))," and overriding ",(0,a.kt)("a",{parentName:"p",href:"/api/BoundTemplate#render_with_context"},(0,a.kt)("inlineCode",{parentName:"a"},"render_with_context()")),"."),(0,a.kt)("h2",{id:"floats-in-ranges"},"Floats in Ranges"),(0,a.kt)("p",null,"If a range literal uses a float literal as its start or stop value, the float literal must have something after the decimal point. This is OK ",(0,a.kt)("inlineCode",{parentName:"p"},"(1.0..3)"),". This is not ",(0,a.kt)("inlineCode",{parentName:"p"},"(1...3)"),". Ruby Liquid will accept either, resulting in a sequence of ",(0,a.kt)("inlineCode",{parentName:"p"},"[1,2,3]"),"."),(0,a.kt)("h2",{id:"indexable-strings"},"Indexable Strings"),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},(0,a.kt)("em",{parentName:"strong"},"See issue ",(0,a.kt)("a",{parentName:"em",href:"https://github.com/jg-rp/liquid/issues/90"},"#90")))),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},(0,a.kt)("em",{parentName:"strong"},"Fixed in version 1.7.0"))," with ",(0,a.kt)("a",{parentName:"p",href:"/api/future-environment"},(0,a.kt)("inlineCode",{parentName:"a"},"liquid.future.Environment")),"."),(0,a.kt)("p",null,"The reference implementation does not allow us to access characters in a string by their index. Python Liquid does."),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Template")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-liquid"},"{% assign x = 'foobar' -%}\n{{ x[0] }}\n{{ x[1] }}\n{{ x[-1] }}\n")),(0,a.kt)("p",null,(0,a.kt)("strong",{parentName:"p"},"Python Liquid output")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain"},"f\no\nr\n")),(0,a.kt)("p",null,"Shopify/liquid will throw an error (in strict mode) for each attempt at accessing a character by its index."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain"},"<Liquid::UndefinedVariable: Liquid error: undefined variable 0>\n<Liquid::UndefinedVariable: Liquid error: undefined variable 1>\n<Liquid::UndefinedVariable: Liquid error: undefined variable -1>\n")))}u.isMDXComponent=!0},3905:(e,t,n)=>{n.d(t,{Zo:()=>u,kt:()=>c});var i=n(7294);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function r(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);t&&(i=i.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,i)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?r(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):r(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function l(e,t){if(null==e)return{};var n,i,a=function(e,t){if(null==e)return{};var n,i,a={},r=Object.keys(e);for(i=0;i<r.length;i++)n=r[i],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(i=0;i<r.length;i++)n=r[i],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var s=i.createContext({}),p=function(e){var t=i.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},u=function(e){var t=p(e.components);return i.createElement(s.Provider,{value:t},e.children)},d={inlineCode:"code",wrapper:function(e){var t=e.children;return i.createElement(i.Fragment,{},t)}},m=i.forwardRef((function(e,t){var n=e.components,a=e.mdxType,r=e.originalType,s=e.parentName,u=l(e,["components","mdxType","originalType","parentName"]),m=p(n),c=a,g=m["".concat(s,".").concat(c)]||m[c]||d[c]||r;return n?i.createElement(g,o(o({ref:t},u),{},{components:n})):i.createElement(g,o({ref:t},u))}));function c(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var r=n.length,o=new Array(r);o[0]=m;var l={};for(var s in t)hasOwnProperty.call(t,s)&&(l[s]=t[s]);l.originalType=e,l.mdxType="string"==typeof e?e:a,o[1]=l;for(var p=2;p<r;p++)o[p]=n[p];return i.createElement.apply(null,o)}return i.createElement.apply(null,n)}m.displayName="MDXCreateElement"}}]);