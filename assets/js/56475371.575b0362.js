"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[2838],{2184:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>l,contentTitle:()=>o,default:()=>d,frontMatter:()=>i,metadata:()=>s,toc:()=>p});var r=n(3117),a=(n(7294),n(3905));const i={},o="Objects and Drops",s={unversionedId:"introduction/objects-and-drops",id:"introduction/objects-and-drops",title:"Objects and Drops",description:"Python Liquid uses getitem internally for resolving property names and accessing items in a sequence. So, if your data is some combination of dictionaries and lists, for example, templates can reference objects as follows.",source:"@site/docs/introduction/objects-and-drops.md",sourceDirName:"introduction",slug:"/introduction/objects-and-drops",permalink:"/liquid/introduction/objects-and-drops",draft:!1,editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/introduction/objects-and-drops.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Render Context",permalink:"/liquid/introduction/render-context"},next:{title:"Strictness",permalink:"/liquid/introduction/strictness"}},l={},p=[{value:"Drop Wrapper",id:"drop-wrapper",level:2},{value:"<code>__liquid__</code>",id:"__liquid__",level:2},{value:"<code>__html__</code>",id:"__html__",level:2}],c={toc:p};function d(e){let{components:t,...n}=e;return(0,a.kt)("wrapper",(0,r.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"objects-and-drops"},"Objects and Drops"),(0,a.kt)("p",null,"Python Liquid uses ",(0,a.kt)("a",{parentName:"p",href:"https://docs.python.org/3/reference/datamodel.html#object.__getitem__"},(0,a.kt)("inlineCode",{parentName:"a"},"__getitem__"))," internally for resolving property names and accessing items in a sequence. So, if your ",(0,a.kt)("a",{parentName:"p",href:"/liquid/introduction/render-context#render-arguments"},"data")," is some combination of dictionaries and lists, for example, templates can reference objects as follows."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-json",metastring:'title="data"',title:'"data"'},'{\n  "products": [\n    {\n      "title": "Some Shoes",\n      "available": 5,\n      "colors": ["blue", "red"]\n    },\n    {\n      "title": "A Hat",\n      "available": 2,\n      "colors": ["grey", "brown"]\n    }\n  ]\n}\n')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-liquid",metastring:'title="template"',title:'"template"'},"{{ products[0].title }}\n{{ products[-2]['available'] }}\n{{ products.last.title }}\n{{ products.first.colors | join: ', ' }}\n")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"Some Shoes\n5\nA Hat\nblue, red\n")),(0,a.kt)("p",null,"Attempting to access properties from a Python class or class instance ",(0,a.kt)("strong",{parentName:"p"},"will not work"),"."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\nclass Product:\n    def __init__(self, title, colors):\n        self.title = title\n        self.colors = colors\n\nproducts = [\n    Product(title="Some Shoes", colors=["blue", "red"]),\n    Product(title="A Hat", colors=["grey", "brown"]),\n]\n\nTemplate("{{ products.first.title }}!").render(products=products)\n')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-plain",metastring:'title="output"',title:'"output"'},"!\n")),(0,a.kt)("p",null,'This is by design, and is one of the reasons Liquid is considered "safe" and "suitable for end users". To expose an object\'s properties we can implement Python\'s ',(0,a.kt)("a",{parentName:"p",href:"https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence"},"Sequence")," or ",(0,a.kt)("a",{parentName:"p",href:"https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping"},"Mapping")," interface."),(0,a.kt)("admonition",{type:"info"},(0,a.kt)("p",{parentName:"admonition"},'Python Liquid\'s equivalent of a "drop", as found in Ruby Liquid, is a Python object that implements the ',(0,a.kt)("a",{parentName:"p",href:"https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence"},"Sequence")," or ",(0,a.kt)("a",{parentName:"p",href:"https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping"},"Mapping")," interface.")),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from collections import abc\nfrom liquid import Template, StrictUndefined\n\nclass User(abc.Mapping):\n    def __init__(\n        self,\n        first_name,\n        last_name,\n        perms,\n    ):\n        self.first_name = first_name\n        self.last_name = last_name\n        self.perms = perms or []\n\n        self._keys = [\n            "first_name",\n            "last_name",\n            "is_admin",\n            "name",\n        ]\n\n    def __getitem__(self, k):\n        if k in self._keys:\n            return getattr(self, k)\n        raise KeyError(k)\n\n    def __iter__(self):\n        return iter(self._keys)\n\n    def __len__(self):\n        return len(self._keys)\n\n    def __str__(self):\n        return f"User(first_name=\'{self.first_name}\', last_name=\'{self.last_name}\')"\n\n    @property\n    def is_admin(self):\n        return "admin" in self.perms\n\n    @property\n    def name(self):\n        return f"{self.first_name} {self.last_name}"\n\n\nuser = User("John", "Smith", ["admin"])\n\nprint(Template("{{ user.first_name }}").render(user=user))  # John\nprint(Template("{{ user.name }}").render(user=user))  # John Smith\nprint(Template("{{ user.is_admin }}").render(user=user))  # true\n\nprint(Template("{{ user.perms[0] }}", undefined=StrictUndefined).render(user=user))\n# UndefinedError: key error: \'perms\', user[perms][0], on line 1\n')),(0,a.kt)("h2",{id:"drop-wrapper"},"Drop Wrapper"),(0,a.kt)("p",null,'One could implement a simple "Drop" wrapper for data access objects like this, while still being explicit about which properties are exposed to templates.'),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},"class Drop(abc.Mapping):\n    def __init__(obj, keys):\n        self.obj = obj\n        self.keys = keys\n\n    def __getitem__(self, k):\n        # Delegate attribute access to self.obj only if `k` is in `self.keys`.\n        if k in self.keys:\n            return getattr(obj, k)\n        raise KeyError(k)\n\n    def __iter__(self):\n        return iter(self.keys)\n\n    def __len__(self):\n        return len(self.keys)\n")),(0,a.kt)("h2",{id:"__liquid__"},(0,a.kt)("inlineCode",{parentName:"h2"},"__liquid__")),(0,a.kt)("p",null,"By implementing a ",(0,a.kt)("inlineCode",{parentName:"p"},"__liquid__")," method, Python objects can behave like primitive Liquid data types. This is useful for situations where you need your Python object to act as an array index, or to be compared to a primitive data type, for example."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Template\n\nclass IntDrop:\n    def __init__(self, val: int):\n        self.val = val\n\n    def __int__(self) -> int:\n        return self.val\n\n    def __str__(self) -> str:\n        return "one"\n\n    def __liquid__(self) -> int:\n        return self.val\n\n\ntemplate = Template(\n    "{% if my_drop < 10 %}"\n    "{{ my_drop }} "\n    "{% endif %}"\n    "{{ some_array[my_drop] }}"\n)\n\ncontext_data = {\n    "my_drop": IntDrop(1),\n    "some_array": ["a", "b", "c"],\n}\n\nprint(template.render(**context_data))  # one b\n')),(0,a.kt)("h2",{id:"__html__"},(0,a.kt)("inlineCode",{parentName:"h2"},"__html__")),(0,a.kt)("p",null,"When ",(0,a.kt)("a",{parentName:"p",href:"/liquid/introduction/auto-escape"},"HTML auto-escaping")," is enabled, an object can be output as an HTML-safe string by implementing an ",(0,a.kt)("inlineCode",{parentName:"p"},"__html__()")," method."),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\n\nclass ListDrop:\n    def __init__(self, somelist):\n        self.items = somelist\n\n    def __str__(self):\n        return f"ListDrop({self.items})"\n\n    def __html__(self):\n        lis = "\\n".join(f"  <li>{item}</li>" for item in self.items)\n        return f"<ul>\\n{lis}\\n</ul>"\n\nenv = Environment(autoescape=True)\ntemplate = env.from_string(r"{{ products }}")\nprint(template.render(products=ListDrop(["Shoe", "Hat", "Ball"])))\n')),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-html",metastring:'title="output"',title:'"output"'},"<ul>\n  <li>Shoe</li>\n  <li>Hat</li>\n  <li>Ball</li>\n</ul>\n")),(0,a.kt)("p",null,"If auto-escaping is not enabled, ",(0,a.kt)("inlineCode",{parentName:"p"},"__html__")," is ignored and the return value of ",(0,a.kt)("inlineCode",{parentName:"p"},"__str__")," is used instead. Explicitly escaping an object using the ",(0,a.kt)("a",{parentName:"p",href:"../language/filters#escape"},"escape")," filter will always yield an escaped version of ",(0,a.kt)("inlineCode",{parentName:"p"},"__str__"),"."))}d.isMDXComponent=!0},3905:(e,t,n)=>{n.d(t,{Zo:()=>c,kt:()=>m});var r=n(7294);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function i(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?i(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):i(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},i=Object.keys(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);for(r=0;r<i.length;r++)n=i[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var l=r.createContext({}),p=function(e){var t=r.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},c=function(e){var t=p(e.components);return r.createElement(l.Provider,{value:t},e.children)},d={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},u=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,i=e.originalType,l=e.parentName,c=s(e,["components","mdxType","originalType","parentName"]),u=p(n),m=a,f=u["".concat(l,".").concat(m)]||u[m]||d[m]||i;return n?r.createElement(f,o(o({ref:t},c),{},{components:n})):r.createElement(f,o({ref:t},c))}));function m(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var i=n.length,o=new Array(i);o[0]=u;var s={};for(var l in t)hasOwnProperty.call(t,l)&&(s[l]=t[l]);s.originalType=e,s.mdxType="string"==typeof e?e:a,o[1]=s;for(var p=2;p<i;p++)o[p]=n[p];return r.createElement.apply(null,o)}return r.createElement.apply(null,n)}u.displayName="MDXCreateElement"}}]);