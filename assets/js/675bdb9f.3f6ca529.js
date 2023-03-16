"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[6506],{8103:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>I,contentTitle:()=>S,default:()=>j,frontMatter:()=>x,metadata:()=>C,toc:()=>O});var a=n(3117),r=n(7294),l=n(3905),i=n(4334),o=n(3735),u=n(6775),p=n(4423),d=n(636),s=n(9200);function m(e){return function(e){return r.Children.map(e,(e=>{if((0,r.isValidElement)(e)&&"value"in e.props)return e;throw new Error(`Docusaurus error: Bad <Tabs> child <${"string"==typeof e.type?e.type:e.type.name}>: all children of the <Tabs> component should be <TabItem>, and every <TabItem> should have a unique "value" prop.`)}))}(e).map((e=>{let{props:{value:t,label:n,attributes:a,default:r}}=e;return{value:t,label:n,attributes:a,default:r}}))}function c(e){const{values:t,children:n}=e;return(0,r.useMemo)((()=>{const e=t??m(n);return function(e){const t=(0,d.l)(e,((e,t)=>e.value===t.value));if(t.length>0)throw new Error(`Docusaurus error: Duplicate values "${t.map((e=>e.value)).join(", ")}" found in <Tabs>. Every value needs to be unique.`)}(e),e}),[t,n])}function f(e){let{value:t,tabValues:n}=e;return n.some((e=>e.value===t))}function g(e){let{queryString:t=!1,groupId:n}=e;const a=(0,u.k6)(),l=function(e){let{queryString:t=!1,groupId:n}=e;if("string"==typeof t)return t;if(!1===t)return null;if(!0===t&&!n)throw new Error('Docusaurus error: The <Tabs> component groupId prop is required if queryString=true, because this value is used as the search param name. You can also provide an explicit value such as queryString="my-search-param".');return n??null}({queryString:t,groupId:n});return[(0,p._X)(l),(0,r.useCallback)((e=>{if(!l)return;const t=new URLSearchParams(a.location.search);t.set(l,e),a.replace({...a.location,search:t.toString()})}),[l,a])]}function h(e){const{defaultValue:t,queryString:n=!1,groupId:a}=e,l=c(e),[i,o]=(0,r.useState)((()=>function(e){let{defaultValue:t,tabValues:n}=e;if(0===n.length)throw new Error("Docusaurus error: the <Tabs> component requires at least one <TabItem> children component");if(t){if(!f({value:t,tabValues:n}))throw new Error(`Docusaurus error: The <Tabs> has a defaultValue "${t}" but none of its children has the corresponding value. Available values are: ${n.map((e=>e.value)).join(", ")}. If you intend to show no default tab, use defaultValue={null} instead.`);return t}const a=n.find((e=>e.default))??n[0];if(!a)throw new Error("Unexpected error: 0 tabValues");return a.value}({defaultValue:t,tabValues:l}))),[u,p]=g({queryString:n,groupId:a}),[d,m]=function(e){let{groupId:t}=e;const n=function(e){return e?`docusaurus.tab.${e}`:null}(t),[a,l]=(0,s.Nk)(n);return[a,(0,r.useCallback)((e=>{n&&l.set(e)}),[n,l])]}({groupId:a}),h=(()=>{const e=u??d;return f({value:e,tabValues:l})?e:null})();(0,r.useLayoutEffect)((()=>{h&&o(h)}),[h]);return{selectedValue:i,selectValue:(0,r.useCallback)((e=>{if(!f({value:e,tabValues:l}))throw new Error(`Can't select invalid tab value=${e}`);o(e),p(e),m(e)}),[p,m,l]),tabValues:l}}var b=n(5730);const y="tabList__CuJ",v="tabItem_LNqP";function k(e){let{className:t,block:n,selectedValue:l,selectValue:u,tabValues:p}=e;const d=[],{blockElementScrollPositionUntilNextRender:s}=(0,o.o5)(),m=e=>{const t=e.currentTarget,n=d.indexOf(t),a=p[n].value;a!==l&&(s(t),u(a))},c=e=>{var t;let n=null;switch(e.key){case"Enter":m(e);break;case"ArrowRight":{const t=d.indexOf(e.currentTarget)+1;n=d[t]??d[0];break}case"ArrowLeft":{const t=d.indexOf(e.currentTarget)-1;n=d[t]??d[d.length-1];break}}null==(t=n)||t.focus()};return r.createElement("ul",{role:"tablist","aria-orientation":"horizontal",className:(0,i.Z)("tabs",{"tabs--block":n},t)},p.map((e=>{let{value:t,label:n,attributes:o}=e;return r.createElement("li",(0,a.Z)({role:"tab",tabIndex:l===t?0:-1,"aria-selected":l===t,key:t,ref:e=>d.push(e),onKeyDown:c,onClick:m},o,{className:(0,i.Z)("tabs__item",v,null==o?void 0:o.className,{"tabs__item--active":l===t})}),n??t)})))}function N(e){let{lazy:t,children:n,selectedValue:a}=e;if(n=Array.isArray(n)?n:[n],t){const e=n.find((e=>e.props.value===a));return e?(0,r.cloneElement)(e,{className:"margin-top--md"}):null}return r.createElement("div",{className:"margin-top--md"},n.map(((e,t)=>(0,r.cloneElement)(e,{key:t,hidden:e.props.value!==a}))))}function T(e){const t=h(e);return r.createElement("div",{className:(0,i.Z)("tabs-container",y)},r.createElement(k,(0,a.Z)({},e,t)),r.createElement(N,(0,a.Z)({},e,t)))}function q(e){const t=(0,b.Z)();return r.createElement(T,(0,a.Z)({key:String(t)},e))}const w="tabItem_Ymn6";function E(e){let{children:t,hidden:n,className:a}=e;return r.createElement("div",{role:"tabpanel",className:(0,i.Z)(w,a),hidden:n},t)}const x={},S="Getting Started",C={unversionedId:"introduction/getting-started",id:"introduction/getting-started",title:"Getting Started",description:"Python Liquid is a Python engine for Liquid, the safe, customer-facing template language for flexible web apps.",source:"@site/docs/introduction/getting-started.mdx",sourceDirName:"introduction",slug:"/introduction/getting-started",permalink:"/liquid/introduction/getting-started",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/introduction/getting-started.mdx",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",next:{title:"Loading Templates",permalink:"/liquid/introduction/loading-templates"}},I={},O=[{value:"Install",id:"install",level:2},{value:"Render",id:"render",level:2},{value:"Configure",id:"configure",level:2},{value:"Environment",id:"environment",level:2}],P={toc:O};function j(e){let{components:t,...n}=e;return(0,l.kt)("wrapper",(0,a.Z)({},P,n,{components:t,mdxType:"MDXLayout"}),(0,l.kt)("h1",{id:"getting-started"},"Getting Started"),(0,l.kt)("p",null,"Python Liquid is a ",(0,l.kt)("a",{parentName:"p",href:"https://www.python.org/"},"Python")," engine for ",(0,l.kt)("a",{parentName:"p",href:"https://shopify.github.io/liquid/"},"Liquid"),", the safe, customer-facing template language for flexible web apps."),(0,l.kt)("p",null,"This page gets you started using Liquid with Python. See ",(0,l.kt)("a",{parentName:"p",href:"/liquid/language/introduction"},"Introduction to Liquid"),", the ",(0,l.kt)("a",{parentName:"p",href:"/liquid/language/filters"},"filter reference")," and the ",(0,l.kt)("a",{parentName:"p",href:"/liquid/language/tags"},"tag reference")," to learn about writing Liquid templates."),(0,l.kt)("h2",{id:"install"},"Install"),(0,l.kt)("p",null,"Install Python Liquid from ",(0,l.kt)("a",{parentName:"p",href:"https://pypi.org/project/python-liquid/"},"PyPi"),":"),(0,l.kt)(q,{groupId:"pypi-manager",mdxType:"Tabs"},(0,l.kt)(E,{value:"pip",label:"pip",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"python -m pip install -U python-liquid\n"))),(0,l.kt)(E,{value:"pipenv",label:"pipenv",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"pipenv install python-liquid\n"))),(0,l.kt)(E,{value:"poetry",label:"poetry",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"poetry add python-liquid\n")))),(0,l.kt)("p",null,"Or ",(0,l.kt)("a",{parentName:"p",href:"https://anaconda.org/conda-forge/python-liquid"},"conda-forge"),":"),(0,l.kt)(q,{groupId:"conda-manager",mdxType:"Tabs"},(0,l.kt)(E,{value:"anaconda",label:"anaconda",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"conda install -c conda-forge python-liquid\n"))),(0,l.kt)(E,{value:"miniconda",label:"miniconda",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"conda install -c conda-forge python-liquid\n"))),(0,l.kt)(E,{value:"miniforge",label:"miniforge",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"conda install python-liquid\n"))),(0,l.kt)(E,{value:"mamba",label:"mamba",mdxType:"TabItem"},(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-bash"},"mamba install python-liquid\n")))),(0,l.kt)("h2",{id:"render"},"Render"),(0,l.kt)("p",null,"Render a template string by creating a ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,l.kt)("inlineCode",{parentName:"a"},"Template"))," and calling its ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#render"},(0,l.kt)("inlineCode",{parentName:"a"},"render()"))," method."),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\ntemplate = Template("Hello, {{ you }}!")\nprint(template.render(you="World"))  # Hello, World!\nprint(template.render(you="Liquid"))  # Hello, Liquid!\n')),(0,l.kt)("p",null,"Keyword arguments passed to ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/BoundTemplate#render"},(0,l.kt)("inlineCode",{parentName:"a"},"render()"))," are available as variables for templates to use in Liquid expressions."),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\ntemplate = Template(\n    "{% for person in people %}"\n    "Hello, {{ person.name }}!\\n"\n    "{% endfor %}"\n)\n\ndata = {\n    "people": [\n        {"name": "John"},\n        {"name": "Sally"},\n    ]\n}\n\nprint(template.render(**data))\n# Hello, John!\n# Hello, Sally!\n')),(0,l.kt)("h2",{id:"configure"},"Configure"),(0,l.kt)("p",null,"Configure template parsing and rendering behavior with extra arguments to ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,l.kt)("inlineCode",{parentName:"a"},"Template")),". The following example renders a template in ",(0,l.kt)("a",{parentName:"p",href:"/liquid/introduction/strictness"},"strict mode")," and will raise an exception whenever an undefined variable is used. See ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,l.kt)("inlineCode",{parentName:"a"},"liquid.Template"))," for all available options."),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\nfrom liquid import Mode\nfrom liquid import StrictUndefined\n\ntemplate = Template(\n    "Hello, {{ you }}!",\n    tolerance=Mode.STRICT,\n    undefined=StrictUndefined,\n)\n\nresult = template.render(you="World")\n')),(0,l.kt)("admonition",{type:"tip"},(0,l.kt)("p",{parentName:"admonition"},"Keep reading to see how to configure an environment once, then load and render templates from it.")),(0,l.kt)("h2",{id:"environment"},"Environment"),(0,l.kt)("p",null,"While ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,l.kt)("inlineCode",{parentName:"a"},"Template"))," can be convenient, more often than not an application will want to configure a single ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,l.kt)("inlineCode",{parentName:"a"},"Environment")),", then load and render templates from it. This is usually more efficient than using ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,l.kt)("inlineCode",{parentName:"a"},"Template"))," directly."),(0,l.kt)("p",null,"All templates rendered from an ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,l.kt)("inlineCode",{parentName:"a"},"Environment"))," will share the environment's configuration. See ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,l.kt)("inlineCode",{parentName:"a"},"liquid.Environment"))," for all available options. Notice that ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,l.kt)("inlineCode",{parentName:"a"},"Environment"))," accepts a ",(0,l.kt)("inlineCode",{parentName:"p"},"loader")," argument, whereas ",(0,l.kt)("a",{parentName:"p",href:"/liquid/api/Template"},(0,l.kt)("inlineCode",{parentName:"a"},"Template"))," does not."),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid import Mode\nfrom liquid import StrictUndefined\nfrom liquid import FileSystemLoader\n\nenv = Environment(\n    tolerance=Mode.STRICT,\n    undefined=StrictUndefined,\n    loader=FileSystemLoader("./templates/"),\n)\n\ntemplate = env.from_string("Hello, {{ you }}!")\nresult = template.render(you="World")\n')))}j.isMDXComponent=!0},3905:(e,t,n)=>{n.d(t,{Zo:()=>d,kt:()=>c});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},l=Object.keys(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(a=0;a<l.length;a++)n=l[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var u=a.createContext({}),p=function(e){var t=a.useContext(u),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},d=function(e){var t=p(e.components);return a.createElement(u.Provider,{value:t},e.children)},s={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},m=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,l=e.originalType,u=e.parentName,d=o(e,["components","mdxType","originalType","parentName"]),m=p(n),c=r,f=m["".concat(u,".").concat(c)]||m[c]||s[c]||l;return n?a.createElement(f,i(i({ref:t},d),{},{components:n})):a.createElement(f,i({ref:t},d))}));function c(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var l=n.length,i=new Array(l);i[0]=m;var o={};for(var u in t)hasOwnProperty.call(t,u)&&(o[u]=t[u]);o.originalType=e,o.mdxType="string"==typeof e?e:r,i[1]=o;for(var p=2;p<l;p++)i[p]=n[p];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}m.displayName="MDXCreateElement"}}]);