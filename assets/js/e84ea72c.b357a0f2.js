"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4080],{6258:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>a,contentTitle:()=>s,default:()=>u,frontMatter:()=>r,metadata:()=>l,toc:()=>o});var t=i(4848),d=i(8453);const r={},s="Undefined Variables",l={id:"guides/undefined-variables",title:"Undefined Variables",description:'When rendering a Liquid template, if a variable name can not be resolved, an instance of liquid.Undefined is used instead. We can customize template rendering behavior by implementing some of Python\'s "magic" methods on a subclass of liquid.Undefined.',source:"@site/docs/guides/undefined-variables.md",sourceDirName:"guides",slug:"/guides/undefined-variables",permalink:"/liquid/guides/undefined-variables",draft:!1,unlisted:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/guides/undefined-variables.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Tag Analysis",permalink:"/liquid/guides/tag-analysis"},next:{title:"Whitespace Suppression",permalink:"/liquid/guides/whitespace-suppression"}},a={},o=[{value:"Default Undefined",id:"default-undefined",level:2},{value:"Strict Undefined",id:"strict-undefined",level:2},{value:"The default filter",id:"the-default-filter",level:2},{value:"Falsy StrictUndefined",id:"falsy-strictundefined",level:2}];function c(e){const n={a:"a",code:"code",em:"em",h1:"h1",h2:"h2",p:"p",pre:"pre",strong:"strong",...(0,d.useMDXComponents)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.h1,{id:"undefined-variables",children:"Undefined Variables"}),"\n",(0,t.jsxs)(n.p,{children:["When rendering a Liquid template, if a variable name can not be resolved, an instance of ",(0,t.jsx)(n.code,{children:"liquid.Undefined"})," is used instead. We can customize template rendering behavior by implementing some of ",(0,t.jsx)(n.a,{href:"https://docs.python.org/3/reference/datamodel.html#basic-customization",children:'Python\'s "magic" methods'})," on a subclass of ",(0,t.jsx)(n.code,{children:"liquid.Undefined"}),"."]}),"\n",(0,t.jsx)(n.h2,{id:"default-undefined",children:"Default Undefined"}),"\n",(0,t.jsxs)(n.p,{children:["All operations on the default ",(0,t.jsx)(n.code,{children:"Undefined"})," type are silently ignored and, when rendered, it produces an empty string. For example, you can access properties and iterate an undefined variable without error."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-liquid",metastring:'title="template"',children:"Hello {{ nosuchthing }}\n{% for thing in nosuchthing %}\n    {{ thing }}\n{% endfor %}\n"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-plain",metastring:'title="output"',children:"Hello\n\n\n\n"})}),"\n",(0,t.jsx)(n.h2,{id:"strict-undefined",children:"Strict Undefined"}),"\n",(0,t.jsxs)(n.p,{children:["When ",(0,t.jsx)(n.code,{children:"liquid.StrictUndefined"})," is passed as the ",(0,t.jsx)(n.code,{children:"undefined"})," argument to ",(0,t.jsx)(n.a,{href:"/liquid/api/Environment",children:(0,t.jsx)(n.code,{children:"Environment"})})," or ",(0,t.jsx)(n.a,{href:"/liquid/api/Template",children:(0,t.jsx)(n.code,{children:"Template"})}),", any operation on an undefined variable will raise an ",(0,t.jsx)(n.code,{children:"UndefinedError"}),"."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:"from liquid import Environment, StrictUndefined\n\nenv = Environment(undefined=StrictUndefined)\ntemplate = env.from_string(\"Hello {{ nosuchthing }}\")\ntemplate.render()\n# UndefinedError: 'nosuchthing' is undefined, on line 1\n"})}),"\n",(0,t.jsx)(n.h2,{id:"the-default-filter",children:"The default filter"}),"\n",(0,t.jsxs)(n.p,{children:["With ",(0,t.jsx)(n.code,{children:"StrictUndefined"}),", the built-in ",(0,t.jsx)(n.a,{href:"/liquid/language/filters#default",children:(0,t.jsx)(n.code,{children:"default"})})," filter does not handle undefined variables the ",(0,t.jsx)(n.a,{href:"https://github.com/Shopify/liquid/issues/1404",children:"way you might expect"}),". The following example will raise an ",(0,t.jsx)(n.code,{children:"UndefinedError"})," if ",(0,t.jsx)(n.code,{children:"username"})," is undefined."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-liquid",children:'Hello {{ username | default: "user" }}\n'})}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:(0,t.jsx)(n.em,{children:"New in version 1.4.0"})})}),"\n",(0,t.jsxs)(n.p,{children:["We can use the built-in ",(0,t.jsx)(n.code,{children:"StrictDefaultUndefined"})," type, which plays nicely with the ",(0,t.jsx)(n.code,{children:"default"})," filter, while still providing strictness elsewhere."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:"from liquid import Environment\nfrom liquid import StrictDefaultUndefined\n\nenv = Environment(undefined=StrictDefaultUndefined)\ntemplate = env.from_string('Hello {{ username | default: \"user\" }}')\nprint(template.render())\n"})}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-plain",metastring:'title="output"',children:"Hello user\n"})}),"\n",(0,t.jsx)(n.h2,{id:"falsy-strictundefined",children:"Falsy StrictUndefined"}),"\n",(0,t.jsxs)(n.p,{children:["It's ",(0,t.jsx)(n.a,{href:"https://github.com/Shopify/liquid/issues/1034",children:"usually not possible"})," to detect undefined variables in a template using an ",(0,t.jsx)(n.a,{href:"../language/tags#if",children:(0,t.jsx)(n.code,{children:"if"})})," tag. In Python Liquid we can implement an ",(0,t.jsx)(n.code,{children:"Undefined"})," type that allows us to write ",(0,t.jsx)(n.code,{children:"{% if nosuchthing %}"})," or ",(0,t.jsx)(n.code,{children:"{% if nosuchthing == 'foo' %}"}),", but still get some strictness when undefined variables are used elsewhere."]}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'from liquid import Environment\nfrom liquid import StrictUndefined\n\n\nclass FalsyStrictUndefined(StrictUndefined):\n    # Properties that don\'t raise an UndefinedError.\n    allowed_properties = frozenset(\n        [\n            "__repr__",\n            "__bool__",\n            "__eq__",\n            "__liquid__",\n            "__class__",\n            "name",\n            "hint",\n            "obj",\n            "msg",\n        ]\n    )\n\n    def __bool__(self) -> bool:\n        return False\n\n    def __eq__(self, other: object) -> bool:\n        return other is False\n\n\nenv = Environment(undefined=FalsyStrictUndefined)\n\ntemplate = env.from_string("{% if nosuchthing %}foo{% else %}bar{% endif %}")\nprint(template.render())  # "bar"\n\ntemplate = env.from_string("{% if nosuchthing == \'hi\' %}foo{% else %}bar{% endif %}")\nprint(template.render())  # "bar"\n\ntemplate = env.from_string("{{ nosuchthing | upcase }}")\ntemplate.render()\n# UndefinedError: \'nosuchthing\' is undefined, on line 1\n'})})]})}function u(e={}){const{wrapper:n}={...(0,d.useMDXComponents)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(c,{...e})}):c(e)}},8453:(e,n,i)=>{i.r(n),i.d(n,{MDXProvider:()=>l,useMDXComponents:()=>s});var t=i(6540);const d={},r=t.createContext(d);function s(e){const n=t.useContext(r);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function l(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(d):e.components||d:s(e.components),t.createElement(r.Provider,{value:n},e.children)}}}]);