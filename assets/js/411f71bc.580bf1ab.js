"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[8062],{3905:(e,t,n)=>{n.r(t),n.d(t,{MDXContext:()=>s,MDXProvider:()=>u,mdx:()=>x,useMDXComponents:()=>p,withMDXComponents:()=>m});var i=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(){return a=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var n=arguments[t];for(var i in n)Object.prototype.hasOwnProperty.call(n,i)&&(e[i]=n[i])}return e},a.apply(this,arguments)}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);t&&(i=i.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,i)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function d(e,t){if(null==e)return{};var n,i,r=function(e,t){if(null==e)return{};var n,i,r={},a=Object.keys(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var s=i.createContext({}),m=function(e){return function(t){var n=p(t.components);return i.createElement(e,a({},t,{components:n}))}},p=function(e){var t=i.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},u=function(e){var t=p(e.components);return i.createElement(s.Provider,{value:t},e.children)},c="mdxType",f={inlineCode:"code",wrapper:function(e){var t=e.children;return i.createElement(i.Fragment,{},t)}},h=i.forwardRef((function(e,t){var n=e.components,r=e.mdxType,a=e.originalType,l=e.parentName,s=d(e,["components","mdxType","originalType","parentName"]),m=p(n),u=r,c=m["".concat(l,".").concat(u)]||m[u]||f[u]||a;return n?i.createElement(c,o(o({ref:t},s),{},{components:n})):i.createElement(c,o({ref:t},s))}));function x(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var a=n.length,l=new Array(a);l[0]=h;var o={};for(var d in t)hasOwnProperty.call(t,d)&&(o[d]=t[d]);o.originalType=e,o[c]="string"==typeof e?e:r,l[1]=o;for(var s=2;s<a;s++)l[s]=n[s];return i.createElement.apply(null,l)}return i.createElement.apply(null,n)}h.displayName="MDXCreateElement"},6859:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>d,contentTitle:()=>l,default:()=>u,frontMatter:()=>a,metadata:()=>o,toc:()=>s});var i=n(7462),r=(n(7294),n(3905));const a={},l="Custom Filters",o={unversionedId:"guides/custom-filters",id:"guides/custom-filters",title:"Custom Filters",description:"In Python Liquid, a filters are implemented as a Python functions or callable classes that accept at least one argument, the left hand side of a filtered expression. The callable's return value will be output, assigned or piped to more filters.",source:"@site/docs/guides/custom-filters.md",sourceDirName:"guides",slug:"/guides/custom-filters",permalink:"/liquid/guides/custom-filters",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/guides/custom-filters.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Caching",permalink:"/liquid/introduction/caching"},next:{title:"Custom Tags",permalink:"/liquid/guides/custom-tags"}},d={},s=[{value:"Add a Filter",id:"add-a-filter",level:2},{value:"With Context",id:"with-context",level:3},{value:"With Environment",id:"with-environment",level:3},{value:"Replace a Filter",id:"replace-a-filter",level:2},{value:"Remove a Filter",id:"remove-a-filter",level:2},{value:"Class-Based Filters",id:"class-based-filters",level:2},{value:"Async Filters",id:"async-filters",level:3},{value:"Filter Function Decorators",id:"filter-function-decorators",level:2},{value:"<code>@liquid_filter</code>",id:"liquid_filter",level:3},{value:"<code>@sequence_filter</code>",id:"sequence_filter",level:3},{value:"<code>@array_filter</code>",id:"array_filter",level:3},{value:"<code>@string_filter</code>",id:"string_filter",level:3},{value:"<code>@math_filter</code>",id:"math_filter",level:3},{value:"Raising Exceptions From Filter Functions",id:"raising-exceptions-from-filter-functions",level:2}],m={toc:s},p="wrapper";function u(e){let{components:t,...n}=e;return(0,r.mdx)(p,(0,i.default)({},m,n,{components:t,mdxType:"MDXLayout"}),(0,r.mdx)("h1",{id:"custom-filters"},"Custom Filters"),(0,r.mdx)("p",null,"In Python Liquid, a ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/language/introduction#filters"},"filters")," are implemented as a Python functions or callable classes that accept at least one argument, the left hand side of a filtered expression. The callable's return value will be output, assigned or piped to more filters."),(0,r.mdx)("admonition",{type:"info"},(0,r.mdx)("p",{parentName:"admonition"},"All built-in filters are implemented in this way, so have a look in ",(0,r.mdx)("a",{parentName:"p",href:"https://github.com/jg-rp/liquid/tree/main/liquid/builtin/filters"},"liquid/builtin/filters/")," for examples.")),(0,r.mdx)("h2",{id:"add-a-filter"},"Add a Filter"),(0,r.mdx)("p",null,"Add a custom template filter to an ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,r.mdx)("inlineCode",{parentName:"a"},"Environment"))," by calling its ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment#add_filter"},(0,r.mdx)("inlineCode",{parentName:"a"},"add_filter()"))," method. Here's a simple example of adding Python's ",(0,r.mdx)("inlineCode",{parentName:"p"},"str.endswith")," as a filter function."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment, FileSystemLoader\n\nenv = Environment(loader=FileSystemLoader("templates/"))\nenv.add_filter("endswith", str.endswith)\n')),(0,r.mdx)("p",null,"In a template, you'd use it like this."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-liquid"},'{% assign foo = "foobar" | endswith: "bar" %}\n{% if foo %}\n    \x3c!-- do something --\x3e\n{% endif %}\n')),(0,r.mdx)("h3",{id:"with-context"},"With Context"),(0,r.mdx)("p",null,"Decorate filter functions with ",(0,r.mdx)("inlineCode",{parentName:"p"},"with_context")," to have the active render context passed as a keyword argument. Notice that we can use the ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/context"},(0,r.mdx)("inlineCode",{parentName:"a"},"context"))," object to resolve variables that have not been passed as filter arguments."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python",metastring:'title="myfilters.py"',title:'"myfilters.py"'},'from liquid.filter import with_context\nfrom liquid.filter import string_filter\n\n@string_filter\n@with_context\ndef link_to_tag(label, tag, *, context):\n    handle = context.resolve("handle", default="")\n    return (\n        f\'<a title="Show tag {tag}" href="/collections/{handle}/{tag}">{label}</a>\'\n    )\n')),(0,r.mdx)("p",null,"And register it wherever you create your environment."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment, FileSystemLoader\nfrom myfilters import link_to_tag\n\nenv = Environment(loader=FileSystemLoader("templates/"))\nenv.add_filter("link_to_tag", link_to_tag)\n')),(0,r.mdx)("p",null,"In a template, you could then use the link_to_tag filter like this."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-liquid"},'{% if tags %}\n    <dl class="navbar">\n    <dt>Tags</dt>\n        {% for tag in collection.tags %}\n        <dd>{{ tag | link_to_tag: tag }}</dd>\n        {% endfor %}\n    </dl>\n{% endif %}\n')),(0,r.mdx)("h3",{id:"with-environment"},"With Environment"),(0,r.mdx)("p",null,"Decorate filter functions with ",(0,r.mdx)("inlineCode",{parentName:"p"},"with_environment")," to have the active ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,r.mdx)("inlineCode",{parentName:"a"},"Environment"))," passed as a keyword argument. For example, the built-in ",(0,r.mdx)("a",{parentName:"p",href:"../language/filters#strip_newlines"},(0,r.mdx)("inlineCode",{parentName:"a"},"strip_newlines"))," filter changes its return value depending on parameters set on the environment."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'@with_environment\n@string_filter\ndef strip_newlines(val: str, *, environment: Environment) -> str:\n    """Return the given string with all newline characters removed."""\n    if environment.autoescape:\n        val = markupsafe_escape(val)\n        return Markup(RE_LINETERM.sub("", val))\n    return RE_LINETERM.sub("", val)\n')),(0,r.mdx)("h2",{id:"replace-a-filter"},"Replace a Filter"),(0,r.mdx)("p",null,"If given the name of an existing filter function, ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment#add_filter"},(0,r.mdx)("inlineCode",{parentName:"a"},"Environment.add_filter()"))," will replace it without warning. For example, suppose you wish to replace the ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/language/filters#slice"},(0,r.mdx)("inlineCode",{parentName:"a"},"slice"))," filter for one which uses start and stop values instead of start and length, and is a bit more forgiving in terms of allowed inputs."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python",metastring:'title="myfilters.py"',title:'"myfilters.py"'},'@liquid_filter\ndef myslice(val, start, stop = None):\n    try:\n        start = int(start)\n    except (ValueError, TypeError) as err:\n        raise FilterArgumentError(\n            f"slice expected an integer start, found {type(start).__name__}"\n        ) from err\n\n    if stop is None:\n        return val[start]\n\n    try:\n        stop = int(stop)\n    except (ValueError, TypeError) as err:\n        raise FilterArgumentError(\n            f"slice expected an integer stop, found {type(stop).__name__}"\n        ) from err\n\n    if isinstance(val, str):\n        return val[start:stop]\n\n    # `val` could be any sequence.\n    return list(val[start:stop])\n')),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment, FileSystemLoader\nfrom myfilters import myslice\n\nenv = Environment(loader=FileSystemLoader("templates/"))\nenv.add_filter("slice", myslice)\n')),(0,r.mdx)("h2",{id:"remove-a-filter"},"Remove a Filter"),(0,r.mdx)("p",null,"Remove a built-in filter by deleting it from ",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/Environment"},(0,r.mdx)("inlineCode",{parentName:"a"},"Environment.filters")),". It's a regular dictionary mapping filter names to filter functions."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment, FileSystemLoader\n\nenv = Environment(loader=FileSystemLoader("templates/"))\ndel env.filters["base64_decode"]\n')),(0,r.mdx)("h2",{id:"class-based-filters"},"Class-Based Filters"),(0,r.mdx)("p",null,"If your custom filter takes initialization arguments or needs to retain state between calls (probably not a good idea), a class-based implementation might be appropriate. Simply implement a ",(0,r.mdx)("a",{parentName:"p",href:"https://docs.python.org/3/reference/datamodel.html#object.__call__"},(0,r.mdx)("inlineCode",{parentName:"a"},"__call__"))," method, and Python Liquid will use it when applying the filter."),(0,r.mdx)("p",null,"For example, here's the implementation of a ",(0,r.mdx)("inlineCode",{parentName:"p"},"json")," filter, that dumps the input object to a JSON formatted string."),(0,r.mdx)("pre",null,(0,r.mdx)("code",{parentName:"pre",className:"language-python"},"import json\nfrom typing import Any\nfrom typing import Callable\nfrom typing import Optional\n\nfrom liquid.filter import int_arg\nfrom liquid.filter import liquid_filter\n\nclass JSON:\n    def __init__(self, default: Optional[Callable[[Any], Any]] = None):\n        self.default = default\n\n    @liquid_filter\n    def __call__(\n        self,\n        obj: object,\n        indent: Optional[object] = None,\n    ) -> str:\n        indent = int_arg(indent) if indent else None\n        return json.dumps(obj, default=self.default, indent=indent)\n")),(0,r.mdx)("h3",{id:"async-filters"},"Async Filters"),(0,r.mdx)("p",null,"Since version 1.9.0, class-based filters can also implement a ",(0,r.mdx)("inlineCode",{parentName:"p"},"filter_async")," method, which should be a coroutine. When applied in an async context, if a filter implements ",(0,r.mdx)("inlineCode",{parentName:"p"},"filter_async"),", it will be awaited instead of calling ",(0,r.mdx)("inlineCode",{parentName:"p"},"__call__"),"."),(0,r.mdx)("h2",{id:"filter-function-decorators"},"Filter Function Decorators"),(0,r.mdx)("p",null,"Although not required, built-in filter functions tend to use decorators for performing common argument manipulation and error handling. None of these decorators take any arguments, and they can all be found in ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.filters"),"."),(0,r.mdx)("h3",{id:"liquid_filter"},(0,r.mdx)("inlineCode",{parentName:"h3"},"@liquid_filter")),(0,r.mdx)("p",null,"A filter function decorator that catches any ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError"),"s raised from the wrapped function. If a ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError")," is raised, it is re-raised as a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterArgumentError"),"."),(0,r.mdx)("h3",{id:"sequence_filter"},(0,r.mdx)("inlineCode",{parentName:"h3"},"@sequence_filter")),(0,r.mdx)("p",null,"A filter function decorator that raises a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterValueError")," if the filter value\ncan not be coerced into an array-like object. Also catches any ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError"),"s raised from the wrapped function. If a ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError")," is raised, it is re-raised as a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterArgumentError"),"."),(0,r.mdx)("p",null,"This is intended to mimic the semantics of the reference implementation's ",(0,r.mdx)("inlineCode",{parentName:"p"},"InputIterator")," class."),(0,r.mdx)("h3",{id:"array_filter"},(0,r.mdx)("inlineCode",{parentName:"h3"},"@array_filter")),(0,r.mdx)("p",null,"A filter function decorator that raises a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterValueError")," if the filter value\nis not array-like. Also catches any ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError"),"s raised from the wrapped function. If a ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError"),"\nis raised, it is re-raised as a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterArgumentError"),"."),(0,r.mdx)("h3",{id:"string_filter"},(0,r.mdx)("inlineCode",{parentName:"h3"},"@string_filter")),(0,r.mdx)("p",null,"A filter function decorator that converts the first positional argument to a string and catches any\n",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError"),"s raised from the wrapped function. If a ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError")," is raised, it is re-raised as a\n",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterArgumentError"),"."),(0,r.mdx)("h3",{id:"math_filter"},(0,r.mdx)("inlineCode",{parentName:"h3"},"@math_filter")),(0,r.mdx)("p",null,"A filter function decorator that raises a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.excpetions.FilterArgumentError")," if the filter\nvalue is not, or can not be converted to, a number. Also catches any ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError"),"s raised from the\nwrapped function. If a ",(0,r.mdx)("inlineCode",{parentName:"p"},"TypeError")," is raised, it is re-raised as a ",(0,r.mdx)("inlineCode",{parentName:"p"},"liquid.exceptions.FilterArgumentError"),"."),(0,r.mdx)("h2",{id:"raising-exceptions-from-filter-functions"},"Raising Exceptions From Filter Functions"),(0,r.mdx)("p",null,"In general, when raising exceptions from filter functions, those exceptions should be a subclass of\n",(0,r.mdx)("a",{parentName:"p",href:"/liquid/api/exceptions#liquidexceptionsfiltererror"},(0,r.mdx)("inlineCode",{parentName:"a"},"liquid.exceptions.FilterError")),"."))}u.isMDXComponent=!0}}]);