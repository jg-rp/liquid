"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[4394],{3905:(e,n,t)=>{t.r(n),t.d(n,{MDXContext:()=>p,MDXProvider:()=>u,mdx:()=>h,useMDXComponents:()=>d,withMDXComponents:()=>s});var i=t(7294);function r(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function o(){return o=Object.assign||function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var i in t)Object.prototype.hasOwnProperty.call(t,i)&&(e[i]=t[i])}return e},o.apply(this,arguments)}function a(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);n&&(i=i.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,i)}return t}function l(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?a(Object(t),!0).forEach((function(n){r(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):a(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function m(e,n){if(null==e)return{};var t,i,r=function(e,n){if(null==e)return{};var t,i,r={},o=Object.keys(e);for(i=0;i<o.length;i++)t=o[i],n.indexOf(t)>=0||(r[t]=e[t]);return r}(e,n);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(i=0;i<o.length;i++)t=o[i],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(r[t]=e[t])}return r}var p=i.createContext({}),s=function(e){return function(n){var t=d(n.components);return i.createElement(e,o({},n,{components:t}))}},d=function(e){var n=i.useContext(p),t=n;return e&&(t="function"==typeof e?e(n):l(l({},n),e)),t},u=function(e){var n=d(e.components);return i.createElement(p.Provider,{value:n},e.children)},c="mdxType",f={inlineCode:"code",wrapper:function(e){var n=e.children;return i.createElement(i.Fragment,{},n)}},x=i.forwardRef((function(e,n){var t=e.components,r=e.mdxType,o=e.originalType,a=e.parentName,p=m(e,["components","mdxType","originalType","parentName"]),s=d(t),u=r,c=s["".concat(a,".").concat(u)]||s[u]||f[u]||o;return t?i.createElement(c,l(l({ref:n},p),{},{components:t})):i.createElement(c,l({ref:n},p))}));function h(e,n){var t=arguments,r=n&&n.mdxType;if("string"==typeof e||r){var o=t.length,a=new Array(o);a[0]=x;var l={};for(var m in n)hasOwnProperty.call(n,m)&&(l[m]=n[m]);l.originalType=e,l[c]="string"==typeof e?e:r,a[1]=l;for(var p=2;p<o;p++)a[p]=t[p];return i.createElement.apply(null,a)}return i.createElement.apply(null,t)}x.displayName="MDXCreateElement"},9853:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>m,contentTitle:()=>a,default:()=>u,frontMatter:()=>o,metadata:()=>l,toc:()=>p});var i=t(7462),r=(t(7294),t(3905));const o={},a="Resource Limits",l={unversionedId:"guides/resource-limits",id:"guides/resource-limits",title:"Resource Limits",description:"_New in version 1.4.0_",source:"@site/docs/guides/resource-limits.md",sourceDirName:"guides",slug:"/guides/resource-limits",permalink:"/liquid/guides/resource-limits",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/guides/resource-limits.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Whitespace Suppression",permalink:"/liquid/guides/whitespace-suppression"},next:{title:"Django Liquid",permalink:"/liquid/guides/django-liquid"}},m={},p=[{value:"Context Depth Limit",id:"context-depth-limit",level:2},{value:"Local Namespace Limit",id:"local-namespace-limit",level:2},{value:"Loop Iteration Limit",id:"loop-iteration-limit",level:2},{value:"Output Stream Limit",id:"output-stream-limit",level:2},{value:"String to Integer Limit",id:"string-to-integer-limit",level:2}],s={toc:p},d="wrapper";function u(e){let{components:n,...t}=e;return(0,r.mdx)(d,(0,i.default)({},s,t,{components:n,mdxType:"MDXLayout"}),(0,r.mdx)("h1",{id:"resource-limits"},"Resource Limits"),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},(0,r.mdx)("em",{parentName:"strong"},"New in version 1.4.0"))),(0,r.mdx)("p",null,"For deployments where template authors are untrusted, you can set limits on some resources to avoid malicious templates from consuming too much memory or too many CPU cycles. Set one or more resource limits by subclassing a Liquid ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},"Environment"),"."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\n\nclass MyEnvironment(Environment):\n    context_depth_limit = 30\n    local_namespace_limit = 2000\n    loop_iteration_limit = 1000\n    output_stream_limit = 15000\n\n\nenv = MyEnvironment()\n\ntemplate = env.from_string("""\\\n{% for x in (1..1000000) %}\n{% for y in (1..1000000) %}\n    {{ x }},{{ y }}\n{% endfor %}\n{% endfor %}\n""")\n\ntemplate.render()\n# LoopIterationLimitError: loop iteration limit reached, on line 1\n')),(0,r.mdx)("h2",{id:"context-depth-limit"},"Context Depth Limit"),(0,r.mdx)("p",null,"The maximum number of times a render context can be extended or wrapped before a ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/exceptions#liquidexceptionscontextdeptherror"},(0,r.mdx)("inlineCode",{parentName:"a"},"ContextDepthError"))," is raised."),(0,r.mdx)("p",null,"This helps us guard against recursive use of the ",(0,r.mdx)("inlineCode",{parentName:"p"},"include")," and ",(0,r.mdx)("inlineCode",{parentName:"p"},"render")," tags. The default context depth limit is 30. Before Python Liquid version 1.4.0, a context depth limit of 30 was hard coded."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom liquid import DictLoader\n\nenv = Environment(\n    loader=DictLoader(\n        {\n            "foo": "{% render \'bar\' %}",\n            "bar": "{% render \'foo\' %}",\n        }\n    )\n)\n\ntemplate = env.from_string("{% render \'foo\' %}")\ntemplate.render()\n# ContextDepthError: maximum context depth reached, possible recursive render, on line 1\n')),(0,r.mdx)("h2",{id:"local-namespace-limit"},"Local Namespace Limit"),(0,r.mdx)("p",null,"The maximum number of bytes (according to ",(0,r.mdx)("inlineCode",{parentName:"p"},"sys.getsizeof()"),") allowed in a template's local namespace, per render, before a ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/exceptions#liquidexceptionslocalnamespacelimiterror"},(0,r.mdx)("inlineCode",{parentName:"a"},"LocalNamespaceLimitError"))," exception is raised. Note that we only count the size of the local namespace values, not its keys."),(0,r.mdx)("p",null,"The default ",(0,r.mdx)("inlineCode",{parentName:"p"},"local_namespace_limit")," is ",(0,r.mdx)("inlineCode",{parentName:"p"},"None"),", meaning there is no limit."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\n\nclass MyEnvironment(Environment):\n    local_namespace_limit = 50  # Very low, for demonstration purposes.\n\nenv = MyEnvironment()\n\ntemplate = env.from_string("""\\\n{% assign x = "Nunc est nulla, pellentesque ac dui id erat curae." %}\n""")\n\ntemplate.render()\n# LocalNamespaceLimitError: local namespace limit reached, on line 1\n')),(0,r.mdx)("admonition",{type:"caution"},(0,r.mdx)("p",{parentName:"admonition"},(0,r.mdx)("a",{parentName:"p",href:"https://doc.pypy.org/en/latest/cpython_differences.html"},"PyPy")," does not implement ",(0,r.mdx)("inlineCode",{parentName:"p"},"sys.getsizeof"),". Instead of a size in bytes, when run with PyPy, ",(0,r.mdx)("inlineCode",{parentName:"p"},"local_namespace_limit")," will degrade to being the number of distinct values in a template's local namespace.")),(0,r.mdx)("p",null,"You can customize the namespace size calculation by subclassing ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/context"},(0,r.mdx)("inlineCode",{parentName:"a"},"Context"))," and overriding ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/context#get_size_of_locals"},(0,r.mdx)("inlineCode",{parentName:"a"},"get_size_of_locals()")),". This example simply counts the number of entries in the namespace."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},"from liquid import Environment\nfrom liquid import Context\nfrom liquid.template import BoundTemplate\n\nclass MyRenderContext(Context):\n    def get_size_of_locals(self) -> int:\n        if not self.env.local_namespace_limit:\n            return 0\n        return len(self.locals) + self.local_namespace_size_carry\n\n\nclass MyBoundTemplate(BoundTemplate):\n    context_class = MyRenderContext\n\n\nclass MyEnvironment(Environment):\n    local_namespace_limit = 2  # XXX: very low, for demonstration purposes\n    template_class = MyBoundTemplate\n\n\nenv = MyEnvironment()\n\ntemplate = env.from_string(\n    \"{% assign foo = 'hello' %}\"\n    \"{% assign bar = 'world' %}\"\n).render()\n\n\n# raises a LocalNamespaceLimitError\ntemplate = env.from_string(\n    \"{% assign foo = 'hello' %}\"\n    \"{% assign bar = 'world' %}\"\n    \"{% assign baz = '!' %}\"\n).render()\n")),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},(0,r.mdx)("em",{parentName:"strong"},"Changed in version 1.4.7"),":")," The default implementation of ",(0,r.mdx)("inlineCode",{parentName:"p"},"get_size_of_locals")," no longer attempts to dedupe local namespace values as it would raise a ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError")," on unhashable types."),(0,r.mdx)("h2",{id:"loop-iteration-limit"},"Loop Iteration Limit"),(0,r.mdx)("p",null,"The maximum number of loop iterations allowed before a ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/exceptions#liquidexceptionsloopiterationlimiterror"},(0,r.mdx)("inlineCode",{parentName:"a"},"LoopIterationLimitError"))," is raised."),(0,r.mdx)("p",null,"The default ",(0,r.mdx)("inlineCode",{parentName:"p"},"loop_iteration_limit")," is ",(0,r.mdx)("inlineCode",{parentName:"p"},"None"),", meaning there is no limit."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\n\nclass MyEnvironment(Environment):\n    loop_iteration_limit = 999\n\n\nenv = MyEnvironment()\n\ntemplate = env.from_string("""\\\n{% for x in (1..100) %}\n{% for y in (1..100) %}\n    {{ x }},{{ y }}\n{% endfor %}\n{% endfor %}\n""")\n\ntemplate.render()\n# LoopIterationLimitError: loop iteration limit reached, on line 1\n')),(0,r.mdx)("p",null,"Other built in tags that contribute to the loop iteration counter are ",(0,r.mdx)("inlineCode",{parentName:"p"},"render"),", ",(0,r.mdx)("inlineCode",{parentName:"p"},"include")," (when using their ",(0,r.mdx)("inlineCode",{parentName:"p"},"{% render 'thing' for some.thing %}")," syntax) and ",(0,r.mdx)("inlineCode",{parentName:"p"},"tablerow"),". If a partial template is rendered within a ",(0,r.mdx)("inlineCode",{parentName:"p"},"for")," loop, the loop counter is carried over to the render context of the partial template."),(0,r.mdx)("h2",{id:"output-stream-limit"},"Output Stream Limit"),(0,r.mdx)("p",null,"The maximum number of bytes that can be written to a template's output stream, per render, before an ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/exceptions#liquidexceptionsoutputstreamlimiterror"},(0,r.mdx)("inlineCode",{parentName:"a"},"OutputStreamLimitError"))," exception is raised."),(0,r.mdx)("p",null,"The default ",(0,r.mdx)("inlineCode",{parentName:"p"},"output_stream_limit")," is ",(0,r.mdx)("inlineCode",{parentName:"p"},"None"),", meaning there is no limit."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\n\nclass MyEnvironment(Environment):\n    output_stream_limit = 20  # Very low, for demonstration purposes.\n\n\nenv = MyEnvironment()\n\ntemplate = env.from_string("""\\\n{% if false %}\nthis is never rendered, so will not contribute the the output byte counter\n{% endif %}\nHello, {{ you }}!\n""")\n\ntemplate.render(you="World")\n# \'\\nHello, World!\\n\'\n\ntemplate.render(you="something longer that exceeds our limit")\n# OutputStreamLimitError: output stream limit reached, on line 4\n')),(0,r.mdx)("h2",{id:"string-to-integer-limit"},"String to Integer Limit"),(0,r.mdx)("p",null,(0,r.mdx)("strong",{parentName:"p"},(0,r.mdx)("em",{parentName:"strong"},"New in version 1.4.4"))),(0,r.mdx)("p",null,(0,r.mdx)("a",{parentName:"p",href:"https://github.com/python/cpython/issues/95778"},"CVE-2020-10735")," describes a potential denial of service attack by converting very long strings to integers. As of version 1.4.4, Python Liquid will raise a ",(0,r.mdx)("inlineCode",{parentName:"p"},"LiquidValueError")," if an attempt is made to cast a long string to an integer."),(0,r.mdx)("p",null,"Due to some unfortunate early Python Liquid design decisions, this is an interpreter-wide limit, unlike other limits described on this page, which are set per ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.Environment"),"."),(0,r.mdx)("p",null,"Python Liquid will look for a ",(0,r.mdx)("inlineCode",{parentName:"p"},"LIQUIDINTMAXSTRDIGITS")," ",(0,r.mdx)("a",{parentName:"p",href:"https://en.wikipedia.org/wiki/Environment_variable"},"environment variable"),", giving the maximum number of digits allowed before attempting a str to int conversion. We will fall back to looking for ",(0,r.mdx)("inlineCode",{parentName:"p"},"PYTHONINTMAXSTRDIGITS")," before defaulting to ",(0,r.mdx)("inlineCode",{parentName:"p"},"4300"),". Use ",(0,r.mdx)("inlineCode",{parentName:"p"},"LIQUIDINTMAXSTRDIGITS")," when you want to use a lower limit for Liquid while keeping Python's limit higher."),(0,r.mdx)("p",null,"When using ",(0,r.mdx)("a",{parentName:"p",href:"https://github.com/python/cpython/pull/96500/files#diff-08a31a70dd1f6d97aa8dacdce77db4de04c700d9949be1af611a595186aad5b3"},"patched versions")," of Python, Liquid will ",(0,r.mdx)("strong",{parentName:"p"},"not")," honour ",(0,r.mdx)("inlineCode",{parentName:"p"},"sys.set_int_max_str_digits"),". If Python's limit is lower than Liquid's, it will be possible to get a ",(0,r.mdx)("inlineCode",{parentName:"p"},"ValueError")," exception instead of a ",(0,r.mdx)("inlineCode",{parentName:"p"},"LiquidValueError")," when parsing Liquid templates."),(0,r.mdx)("admonition",{type:"caution"},(0,r.mdx)("p",{parentName:"admonition"},"Python Liquid's default limit helps guard against malicious templates authors. Be sure to validate user controlled inputs that might appear in a Liquid render context.")))}u.isMDXComponent=!0}}]);