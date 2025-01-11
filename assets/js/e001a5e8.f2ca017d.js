"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[5996],{7985:(n,e,a)=>{a.r(e),a.d(e,{assets:()=>l,contentTitle:()=>o,default:()=>g,frontMatter:()=>r,metadata:()=>s,toc:()=>d});const s=JSON.parse('{"id":"guides/tag-analysis","title":"Tag Analysis","description":"_New in version 1.7.0_","source":"@site/docs/guides/tag-analysis.md","sourceDirName":"guides","slug":"/guides/tag-analysis","permalink":"/liquid/guides/tag-analysis","draft":false,"unlisted":false,"editUrl":"https://github.com/jg-rp/liquid/tree/docs/docs/guides/tag-analysis.md","tags":[],"version":"current","frontMatter":{},"sidebar":"docsSidebar","previous":{"title":"Contextual Template Analysis","permalink":"/liquid/guides/contextual-template-analysis"},"next":{"title":"Undefined Variables","permalink":"/liquid/guides/undefined-variables"}}');var t=a(4848),i=a(8453);const r={},o="Tag Analysis",l={},d=[{value:"Tags",id:"tags",level:2},{value:"All Tags",id:"all-tags",level:2},{value:"Unclosed Tags",id:"unclosed-tags",level:2},{value:"Unexpected Tags",id:"unexpected-tags",level:2},{value:"Unknown Tags",id:"unknown-tags",level:2}];function c(n){const e={a:"a",admonition:"admonition",code:"code",em:"em",h1:"h1",h2:"h2",header:"header",p:"p",pre:"pre",strong:"strong",...(0,i.useMDXComponents)(),...n.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(e.header,{children:(0,t.jsx)(e.h1,{id:"tag-analysis",children:"Tag Analysis"})}),"\n",(0,t.jsx)(e.p,{children:(0,t.jsx)(e.strong,{children:(0,t.jsx)(e.em,{children:"New in version 1.7.0"})})}),"\n",(0,t.jsxs)(e.p,{children:["Use ",(0,t.jsx)(e.a,{href:"/liquid/api/Environment#analyze_tags",children:(0,t.jsx)(e.code,{children:"Environment.analyze_tags()"})}),", ",(0,t.jsx)(e.a,{href:"/liquid/api/Environment#analyze_tags_async",children:(0,t.jsx)(e.code,{children:"Environment.analyze_tags_async()"})})," or ",(0,t.jsx)(e.a,{href:"/liquid/api/Environment#analyze_tags_from_string",children:(0,t.jsx)(e.code,{children:"Environment.analyze_tags_from_string()"})})," to analyze template source text and report tag usage and issues."]}),"\n",(0,t.jsxs)(e.p,{children:["Unlike ",(0,t.jsx)(e.a,{href:"/liquid/guides/static-template-analysis",children:"static template analysis"}),", which also includes tag usage, ",(0,t.jsx)(e.em,{children:"tag analysis"})," operates on tokens generated from template source text, before creating an abstract syntax tree. This give us the opportunity to find unknown, unexpected and unbalanced tags that might cause the parser to raise an exception or skip template blocks."]}),"\n",(0,t.jsx)(e.admonition,{type:"info",children:(0,t.jsxs)(e.p,{children:["Because this form of tag analysis happens before a template is fully parsed, it will never attempt to load and analyze partial templates from ",(0,t.jsx)(e.code,{children:"{% include %}"})," or ",(0,t.jsx)(e.code,{children:"{% render %}"})," tags. Nor is it able to count template variables and filters, like ",(0,t.jsx)(e.a,{href:"/liquid/guides/static-template-analysis",children:(0,t.jsx)(e.code,{children:"BoundTemplate.analyze()"})})," does."]})}),"\n",(0,t.jsx)(e.h2,{id:"tags",children:"Tags"}),"\n",(0,t.jsxs)(e.p,{children:["The object returned from ",(0,t.jsx)(e.code,{children:"analyze_tags()"})," is an instance of ",(0,t.jsx)(e.a,{href:"/liquid/api/tag-analysis",children:(0,t.jsx)(e.code,{children:"TagAnalysis"})}),". Its ",(0,t.jsx)(e.code,{children:"tags"})," property is a dictionary mapping tag names to a list of ",(0,t.jsx)(e.code,{children:"(template_name, line_number)"})," tuples, one tuple for each occurrence of the tag. ",(0,t.jsx)(e.code,{children:"TagAnalysis.tags"}),' includes unknown tags, but excludes "end" and ',(0,t.jsx)(e.em,{children:"inner"})," tags (",(0,t.jsx)(e.code,{children:"else"})," and ",(0,t.jsx)(e.code,{children:"break"})," in this example)."]}),"\n",(0,t.jsx)(e.pre,{children:(0,t.jsx)(e.code,{className:"language-python",children:"from liquid import Environment\n\nenv = Environment()\n\ntag_analysis = env.analyze_tags_from_string(\n    \"\"\"\\\n{% for foo in bar %}\n    {% if foo %}\n        {{ foo | upcase }}\n    {% else %}\n        {% break %}\n    {% endif %}\n{% endfor %}\n\"\"\"\n)\n\nprint(tag_analysis.tags)\n# {'for': [('<string>', 1)], 'if': [('<string>', 2)]}\n"})}),"\n",(0,t.jsx)(e.h2,{id:"all-tags",children:"All Tags"}),"\n",(0,t.jsxs)(e.p,{children:["The ",(0,t.jsx)(e.code,{children:"all_tags"})," property of ",(0,t.jsx)(e.code,{children:"TagAnalysis"}),' is a mapping of tag names to their locations, including "end" tags and inner tags.']}),"\n",(0,t.jsx)(e.pre,{children:(0,t.jsx)(e.code,{className:"language-python",children:"from pprint import pprint\nfrom liquid import Environment\n\nenv = Environment()\n\ntag_analysis = env.analyze_tags_from_string(\n    \"\"\"\\\n{% for foo in bar %}\n    {% if foo %}\n        {{ foo | upcase }}\n    {% endif %}\n{% endfor %}\n\"\"\"\n)\n\npprint(tag_analysis.all_tags)\n# {'endfor': [('<string>', 5)],\n#  'endif': [('<string>', 4)],\n#  'for': [('<string>', 1)],\n#  'if': [('<string>', 2)]}\n"})}),"\n",(0,t.jsx)(e.h2,{id:"unclosed-tags",children:"Unclosed Tags"}),"\n",(0,t.jsxs)(e.p,{children:["The ",(0,t.jsx)(e.code,{children:"unclosed_tags"})," property of ",(0,t.jsx)(e.code,{children:"TagAnalysis"}),' includes the names and locations of block tags that do not have a matching "end" tag.']}),"\n",(0,t.jsx)(e.pre,{children:(0,t.jsx)(e.code,{className:"language-python",children:'from liquid import Environment\n\nenv = Environment()\n\ntag_analysis = env.analyze_tags_from_string(\n    """\\\n{% for foo in bar %}\n    {% if foo %}\n        {{ foo | upcase }}\n    {% endif %}\n"""\n)\n\nprint(tag_analysis.unclosed_tags)\n# {\'for\': [(\'<string>\', 1)]}\n'})}),"\n",(0,t.jsx)(e.h2,{id:"unexpected-tags",children:"Unexpected Tags"}),"\n",(0,t.jsxs)(e.p,{children:["The ",(0,t.jsx)(e.code,{children:"unexpected_tags"})," property of ",(0,t.jsx)(e.code,{children:"TagAnalysis"})," includes the names and locations of ",(0,t.jsx)(e.em,{children:"inner"})," tags that do not have an appropriate enclosing block tag. Like an ",(0,t.jsx)(e.code,{children:"{% else %}"})," appearing outside an ",(0,t.jsx)(e.code,{children:"{% if %}"})," or ",(0,t.jsx)(e.code,{children:"{% unless %}"})," block, for example."]}),"\n",(0,t.jsx)(e.admonition,{type:"caution",children:(0,t.jsxs)(e.p,{children:[(0,t.jsx)(e.code,{children:"unexpected_tags"}),' does not handle the possibility of an "inner" tag appearing in a partial template (using ',(0,t.jsx)(e.code,{children:"{% include %}"}),"), where an appropriate enclosing block is in a parent template."]})}),"\n",(0,t.jsx)(e.pre,{children:(0,t.jsx)(e.code,{className:"language-python",children:'from liquid import Environment\n\nenv = Environment()\n\ntag_analysis = env.analyze_tags_from_string(\n    """\\\n{% for foo in bar %}\n  {{ foo }}\n{% endfor %}\n{% break %}\n"""\n)\n\nprint(tag_analysis.unexpected_tags)\n# {\'break\': [(\'<string>\', 4)]}\n'})}),"\n",(0,t.jsx)(e.h2,{id:"unknown-tags",children:"Unknown Tags"}),"\n",(0,t.jsxs)(e.p,{children:[(0,t.jsx)(e.code,{children:"TagAnalysis.unknown_tags"}),' contains the names and locations of tags that are not registered with the environment. If there\'s an unregistered block tag, only the tag starting the block will be reported. In the case of an "end" tag typo, the "end" tag will be reported as "unknown" and the start tag will be in ',(0,t.jsx)(e.a,{href:"#unclosed-tags",children:(0,t.jsx)(e.code,{children:"unclosed_tags"})}),"."]}),"\n",(0,t.jsx)(e.pre,{children:(0,t.jsx)(e.code,{className:"language-python",children:'from liquid import Environment\n\nenv = Environment()\n\ntag_analysis = env.analyze_tags_from_string(\n    """\\\n{% form article %}\n  <h2>Leave a comment</h2>\n  <input type="submit" value="Post comment" id="comment-submit" />\n{% endform %}\n"""\n)\n\nprint(tag_analysis.unknown_tags)\n# {\'form\': [(\'<string>\', 1)]}\n'})})]})}function g(n={}){const{wrapper:e}={...(0,i.useMDXComponents)(),...n.components};return e?(0,t.jsx)(e,{...n,children:(0,t.jsx)(c,{...n})}):c(n)}},8453:(n,e,a)=>{a.r(e),a.d(e,{MDXProvider:()=>o,useMDXComponents:()=>r});var s=a(6540);const t={},i=s.createContext(t);function r(n){const e=s.useContext(i);return s.useMemo((function(){return"function"==typeof n?n(e):{...e,...n}}),[e,n])}function o(n){let e;return e=n.disableParentContext?"function"==typeof n.components?n.components(t):n.components||t:r(n.components),s.createElement(i.Provider,{value:e},n.children)}}}]);