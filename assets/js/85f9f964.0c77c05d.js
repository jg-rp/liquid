"use strict";(self.webpackChunkliquid_docs=self.webpackChunkliquid_docs||[]).push([[546],{3905:function(e,t,n){n.d(t,{Zo:function(){return d},kt:function(){return u}});var a=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function o(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?o(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):o(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function s(e,t){if(null==e)return{};var n,a,r=function(e,t){if(null==e)return{};var n,a,r={},o=Object.keys(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)n=o[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var l=a.createContext({}),p=function(e){var t=a.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},d=function(e){var t=p(e.components);return a.createElement(l.Provider,{value:t},e.children)},m={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},c=a.forwardRef((function(e,t){var n=e.components,r=e.mdxType,o=e.originalType,l=e.parentName,d=s(e,["components","mdxType","originalType","parentName"]),c=p(n),u=r,f=c["".concat(l,".").concat(u)]||c[u]||m[u]||o;return n?a.createElement(f,i(i({ref:t},d),{},{components:n})):a.createElement(f,i({ref:t},d))}));function u(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var o=n.length,i=new Array(o);i[0]=c;var s={};for(var l in t)hasOwnProperty.call(t,l)&&(s[l]=t[l]);s.originalType=e,s.mdxType="string"==typeof e?e:r,i[1]=s;for(var p=2;p<o;p++)i[p]=n[p];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}c.displayName="MDXCreateElement"},166:function(e,t,n){n.r(t),n.d(t,{frontMatter:function(){return s},contentTitle:function(){return l},metadata:function(){return p},toc:function(){return d},default:function(){return c}});var a=n(7462),r=n(3366),o=(n(7294),n(3905)),i=["components"],s={},l="Custom Loaders",p={unversionedId:"guides/custom-loaders",id:"guides/custom-loaders",title:"Custom Loaders",description:"Loaders are responsible for finding a template's source text given a name or identifier. Built-in",source:"@site/docs/guides/custom-loaders.md",sourceDirName:"guides",slug:"/guides/custom-loaders",permalink:"/liquid/guides/custom-loaders",editUrl:"https://github.com/jg-rp/liquid/tree/docs/docs/guides/custom-loaders.md",tags:[],version:"current",frontMatter:{},sidebar:"docsSidebar",previous:{title:"Custom Tags",permalink:"/liquid/guides/custom-tags"},next:{title:"Security",permalink:"/liquid/guides/security"}},d=[{value:"Loading Sections and Snippets",id:"loading-sections-and-snippets",children:[],level:2},{value:"Loading with Context",id:"loading-with-context",children:[],level:2},{value:"Front Matter Loader",id:"front-matter-loader",children:[],level:2},{value:"Async Database Loader",id:"async-database-loader",children:[],level:2},{value:"File Extension Loader",id:"file-extension-loader",children:[],level:2}],m={toc:d};function c(e){var t=e.components,n=(0,r.Z)(e,i);return(0,o.kt)("wrapper",(0,a.Z)({},m,n,{components:t,mdxType:"MDXLayout"}),(0,o.kt)("h1",{id:"custom-loaders"},"Custom Loaders"),(0,o.kt)("p",null,"Loaders are responsible for finding a template's source text given a name or identifier. Built-in\nloaders include a ",(0,o.kt)("a",{parentName:"p",href:"../api/filesystemloader"},"FileSystemLoader"),", a ",(0,o.kt)("a",{parentName:"p",href:"../api/FileExtensionLoader"},"FileExtensionLoader"),", a ",(0,o.kt)("a",{parentName:"p",href:"../api/choiceloader"},"ChoiceLoader")," and a ",(0,o.kt)("a",{parentName:"p",href:"../api/dictloader"},"DictLoader"),". You might want to write a custom loader to load templates from a database or add extra meta data to the template context, for example."),(0,o.kt)("p",null,"Write a custom loader class by inheriting from ",(0,o.kt)("inlineCode",{parentName:"p"},"liquid.loaders.BaseLoader")," and implementing its\n",(0,o.kt)("inlineCode",{parentName:"p"},"get_source")," method. Then pass an instance of your loader to a ",(0,o.kt)("a",{parentName:"p",href:"../api/Environment"},"liquid.Environment"),"\nas the ",(0,o.kt)("inlineCode",{parentName:"p"},"loader")," argument."),(0,o.kt)("p",null,"We could implement our own version of ",(0,o.kt)("inlineCode",{parentName:"p"},"DictLoader")," like this."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="myloaders.py"',title:'"myloaders.py"'},"from typing import TYPE_CHECKING\nfrom typing import Dict\n\nfrom liquid.loaders import BaseLoader\nfrom liquid.loaders import TemplateSource\nfrom liquid.exceptions import TemplateNotFound\n\nif TYPE_CHECKING:\n    from liquid import Environment\n\nclass DictLoader(BaseLoader):\n    def __init__(self, templates: Dict[str, str]):\n        self.templates = templates\n\n    def get_source(self, _: Environment, template_name: str) -> TemplateSource:\n        try:\n            source = self.templates[template_name]\n        except KeyError as err:\n            raise TemplateNotFound(template_name) from err\n\n        return TemplateSource(source, template_name, None)\n")),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"TemplateSource")," is a named tuple containing the template source as a string, its name and an\noptional ",(0,o.kt)("inlineCode",{parentName:"p"},"uptodate")," callable. If ",(0,o.kt)("inlineCode",{parentName:"p"},"uptodate")," is not ",(0,o.kt)("inlineCode",{parentName:"p"},"None")," it should be a callable that returns\n",(0,o.kt)("inlineCode",{parentName:"p"},"False")," if the template needs to be loaded again, or ",(0,o.kt)("inlineCode",{parentName:"p"},"True")," otherwise."),(0,o.kt)("p",null,"You could then use ",(0,o.kt)("inlineCode",{parentName:"p"},"DictLoader")," like this."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'from liquid import Environment\nfrom myloaders import DictLoader\n\nsnippets = {\n    "greeting": "Hello {{ user.name }}",\n    "row": """\n        <div class="row"\'\n            <div class="col">\n            {{ row_content }}\n            </div>\n        </div>\n        """,\n}\n\nenv = Environment(loader=DictLoader(snippets))\n\ntemplate = env.from_string("""\n    <html>\n        {% include \'greeting\' %}\n        {% for i in (1..3) %}\n        {% include \'row\' with i as row_content %}\n        {% endfor %}\n    </html>\n""")\n\nprint(template.render(user={"name": "Brian"}))\n')),(0,o.kt)("h2",{id:"loading-sections-and-snippets"},"Loading Sections and Snippets"),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},(0,o.kt)("em",{parentName:"strong"},"New in version 1.1.3"))),(0,o.kt)("p",null,"Custom loaders can reference the name of the tag that's trying to load a template, if used from a tag like ",(0,o.kt)("inlineCode",{parentName:"p"},"{% include 'template_name' %}")," or ",(0,o.kt)("inlineCode",{parentName:"p"},"{% render 'template_name' %}"),", or any custom tag that uses ",(0,o.kt)("inlineCode",{parentName:"p"},"Context.get_template_with_context()"),"."),(0,o.kt)("p",null,'This is useful for situations where you want to load partial templates (or "snippets" or "sections") from sub folders within an existing search path, without requiring template authors to include sub folder names in every ',(0,o.kt)("inlineCode",{parentName:"p"},"include")," or ",(0,o.kt)("inlineCode",{parentName:"p"},"render")," tag."),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"BaseLoader.get_source_with_context()")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"BaseLoader.get_source_with_context_async()")," where added in Python Liquid version 1.1.3. These methods are similar to ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source()")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source_async()"),", but are passed the active render context instead of an environment, and arbitrary keyword arguments that can be used by a loader to modify its search space. Their default implementations ignore context and keyword arguments, simply delegating to ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source()")," or ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source_async()"),"."),(0,o.kt)("div",{className:"admonition admonition-note alert alert--secondary"},(0,o.kt)("div",{parentName:"div",className:"admonition-heading"},(0,o.kt)("h5",{parentName:"div"},(0,o.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,o.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,o.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.3 5.69a.942.942 0 0 1-.28-.7c0-.28.09-.52.28-.7.19-.18.42-.28.7-.28.28 0 .52.09.7.28.18.19.28.42.28.7 0 .28-.09.52-.28.7a1 1 0 0 1-.7.3c-.28 0-.52-.11-.7-.3zM8 7.99c-.02-.25-.11-.48-.31-.69-.2-.19-.42-.3-.69-.31H6c-.27.02-.48.13-.69.31-.2.2-.3.44-.31.69h1v3c.02.27.11.5.31.69.2.2.42.31.69.31h1c.27 0 .48-.11.69-.31.2-.19.3-.42.31-.69H8V7.98v.01zM7 2.3c-3.14 0-5.7 2.54-5.7 5.68 0 3.14 2.56 5.7 5.7 5.7s5.7-2.55 5.7-5.7c0-3.15-2.56-5.69-5.7-5.69v.01zM7 .98c3.86 0 7 3.14 7 7s-3.14 7-7 7-7-3.12-7-7 3.14-7 7-7z"}))),"note")),(0,o.kt)("div",{parentName:"div",className:"admonition-content"},(0,o.kt)("p",{parentName:"div"},(0,o.kt)("inlineCode",{parentName:"p"},"Context.get_template_with_context()")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"Context.get_template_with_context_async()")," do not use the default template cache. The environment that manages the default template cache does not know what context variables and keyword arguments might be used to manipulate the search space or loaded template."))),(0,o.kt)("p",null,"This example extends ",(0,o.kt)("a",{parentName:"p",href:"../api/FileExtensionLoader"},"FileExtensionLoader"),", making ",(0,o.kt)("inlineCode",{parentName:"p"},".liquid")," optional, and searches ",(0,o.kt)("inlineCode",{parentName:"p"},"./snippets/")," (relative to the loaders search path) for templates when rendering with the built-in ",(0,o.kt)("inlineCode",{parentName:"p"},"include")," tag."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'from pathlib import Path\n\nfrom liquid import Context\nfrom liquid.loaders import TemplateSource\nfrom liquid.loaders import FileExtensionLoader\n\nclass SnippetsFileSystemLoader(FileExtensionLoader):\n    def get_source_with_context(\n        self,\n        context: Context,\n        template_name: str,\n        **kwargs: str,\n    ) -> TemplateSource:\n        if kwargs.get("tag") == "include":\n            section = Path("snippets").joinpath(template_name)\n            return super().get_source(context.env, str(section))\n        return super().get_source(context.env, template_name)\n')),(0,o.kt)("p",null,(0,o.kt)("inlineCode",{parentName:"p"},"tag")," being parse as a keyword argument is a convention used by the built-in ",(0,o.kt)("inlineCode",{parentName:"p"},"include")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"render")," tags. Any custom tag is free to pass whatever keyword arguments they wish to ",(0,o.kt)("inlineCode",{parentName:"p"},"Context.get_template_with_context()"),", and they will be passed on to ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source_with_context()")," of the configured loader."),(0,o.kt)("div",{className:"admonition admonition-tip alert alert--success"},(0,o.kt)("div",{parentName:"div",className:"admonition-heading"},(0,o.kt)("h5",{parentName:"div"},(0,o.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,o.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"12",height:"16",viewBox:"0 0 12 16"},(0,o.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M6.5 0C3.48 0 1 2.19 1 5c0 .92.55 2.25 1 3 1.34 2.25 1.78 2.78 2 4v1h5v-1c.22-1.22.66-1.75 2-4 .45-.75 1-2.08 1-3 0-2.81-2.48-5-5.5-5zm3.64 7.48c-.25.44-.47.8-.67 1.11-.86 1.41-1.25 2.06-1.45 3.23-.02.05-.02.11-.02.17H5c0-.06 0-.13-.02-.17-.2-1.17-.59-1.83-1.45-3.23-.2-.31-.42-.67-.67-1.11C2.44 6.78 2 5.65 2 5c0-2.2 2.02-4 4.5-4 1.22 0 2.36.42 3.22 1.19C10.55 2.94 11 3.94 11 5c0 .66-.44 1.78-.86 2.48zM4 14h5c-.23 1.14-1.3 2-2.5 2s-2.27-.86-2.5-2z"}))),"tip")),(0,o.kt)("div",{parentName:"div",className:"admonition-content"},(0,o.kt)("p",{parentName:"div"},"These examples could easily have used the ",(0,o.kt)("inlineCode",{parentName:"p"},"render")," tag instead of or as well as ",(0,o.kt)("inlineCode",{parentName:"p"},"include"),"."))),(0,o.kt)("p",null,"This example leaves the ",(0,o.kt)("inlineCode",{parentName:"p"},"include")," tag's search path alone, instead defining a ",(0,o.kt)("inlineCode",{parentName:"p"},"section")," tag that inherits from ",(0,o.kt)("inlineCode",{parentName:"p"},"include")," and searches for templates in the ",(0,o.kt)("inlineCode",{parentName:"p"},"sections/")," subfolder of ",(0,o.kt)("inlineCode",{parentName:"p"},"templates/"),"."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'from pathlib import Path\n\nfrom liquid import Context\nfrom liquid import Environment\nfrom liquid.loaders import FileExtensionLoader\nfrom liquid.loaders import TemplateSource\nfrom liquid.builtin.tags.include_tag import IncludeNode\nfrom liquid.builtin.tags.include_tag import IncludeTag\n\nclass SectionNode(IncludeNode):\n    tag = "section"\n\nclass SectionTag(IncludeTag):\n    name = "section"\n    node_class = SectionNode\n\nclass SectionFileSystemLoader(FileExtensionLoader):\n    def get_source_with_context(\n        self,\n        context: Context,\n        template_name: str,\n        **kwargs: str,\n    ) -> TemplateSource:\n        if kwargs.get("tag") == "section":\n            section = Path("sections").joinpath(template_name)\n            return super().get_source(context.env, str(section))\n        return super().get_source(context.env, template_name)\n\nenv = Environment(loader=SectionFileSystemLoader(search_path="templates/"))\nenv.add_tag(SectionTag)\n')),(0,o.kt)("h2",{id:"loading-with-context"},"Loading with Context"),(0,o.kt)("p",null,(0,o.kt)("strong",{parentName:"p"},(0,o.kt)("em",{parentName:"strong"},"New in version 1.1.3"))),(0,o.kt)("p",null,"When using Liquid in multi-user applications, a loader might need to narrow its search space depending on the current user. The classic example being Shopify, where, to be able to find the appropriate template, the loader must know what the current store ID is."),(0,o.kt)("p",null,"A loader can reference the current render context by implementing ",(0,o.kt)("inlineCode",{parentName:"p"},"BaseLoader.get_source_with_context()")," and/or ",(0,o.kt)("inlineCode",{parentName:"p"},"BaseLoader.get_source_with_context_async()"),". This example gets a ",(0,o.kt)("inlineCode",{parentName:"p"},"site_id")," from the active render context and uses it in combination with the template's name to query an SQLite database. It assumes a table called ",(0,o.kt)("inlineCode",{parentName:"p"},"templates")," exists with columns ",(0,o.kt)("inlineCode",{parentName:"p"},"source"),", ",(0,o.kt)("inlineCode",{parentName:"p"},"updated"),", ",(0,o.kt)("inlineCode",{parentName:"p"},"name")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"site_id"),"."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'import sqlite3\nimport functools\n\nfrom liquid import Context\nfrom liquid.loaders import BaseLoader\nfrom liquid.loaders import TemplateSource\nfrom liquid.exceptions import TemplateNotFound\n\nclass SQLiteLoader(BaseLoader):\n    def __init__(self, con: sqlite3.Connection):\n        self.con = con\n\n    def get_source_with_context(\n        self, context: Context, template_name: str, **kwargs: str\n    ) -> TemplateSource:\n        site_id = context.resolve("site_id")\n        cur = self.con.cursor()\n        cur.execute(\n            "SELECT source, updated "\n            "FROM templates "\n            "WHERE name = ? "\n            "AND site_id = ?",\n            [template_name, site_id],\n        )\n\n        source = cur.fetchone()\n        if not source:\n            raise TemplateNotFound(template_name)\n\n        return TemplateSource(\n            source=source[0],\n            filename=template_name,\n            uptodate=functools.partial(\n                self._is_site_up_to_date,\n                name=template_name,\n                site_id=site_id,\n                updated=source[1],\n            ),\n        )\n\n    def get_source(self, env: Environment, template_name: str) -> TemplateSource:\n        cur = self.con.cursor()\n        cur.execute(\n            "SELECT source, updated FROM templates WHERE name = ?",\n            [template_name],\n        )\n\n        source = cur.fetchone()\n        if not source:\n            raise TemplateNotFound(template_name)\n\n        return TemplateSource(\n            source=source[0],\n            filename=template_name,\n            uptodate=functools.partial(\n                self._is_up_to_date,\n                name=template_name,\n                updated=source[1],\n            ),\n        )\n\n    def _is_site_up_to_date(self, name: str, site_id: int, updated: str) -> bool:\n        cur = self.con.cursor()\n        cur.execute(\n            "SELECT updated FROM templates WHERE name = ? AND site_id = ?",\n            [name, site_id],\n        )\n\n        row = cur.fetchone()\n        if not row:\n            return False\n        return updated == row[0]\n\n    def _is_up_to_date(self, name: str, updated: str) -> bool:\n        cur = self.con.cursor()\n        cur.execute(\n            "SELECT updated FROM templates WHERE name = ?",\n            [name],\n        )\n\n        row = cur.fetchone()\n        if not row:\n            return False\n        return updated == row[0]\n')),(0,o.kt)("h2",{id:"front-matter-loader"},"Front Matter Loader"),(0,o.kt)("p",null,"Loaders can add to a template's render context using the ",(0,o.kt)("inlineCode",{parentName:"p"},"matter")," argument to ",(0,o.kt)("inlineCode",{parentName:"p"},"TemplateSource"),". This example implements a Jekyll style front matter loader."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'import re\nimport yaml  # Assumes pyyaml is installed\n\nfrom liquid import Environment\nfrom liquid.loaders import FileSystemLoader\nfrom liquid.loaders import TemplateSource\n\nRE_FRONT_MATTER = re.compile(r"\\s*---\\s*(.*?)\\s*---\\s*", re.MULTILINE | re.DOTALL)\n\n\nclass FrontMatterFileSystemLoader(FileSystemLoader):\n    def get_source(\n        self,\n        env: Environment,\n        template_name: str,\n    ) -> TemplateSource:\n        source, filename, uptodate, matter = super().get_source(env, template_name)\n        match = RE_FRONT_MATTER.search(source)\n\n        if match:\n            # Should add some yaml error handling here.\n            matter = yaml.load(match.group(1), Loader=yaml.Loader)\n            source = source[match.end() :]\n\n        return TemplateSource(\n            source,\n            filename,\n            uptodate,\n            matter,\n        )\n')),(0,o.kt)("h2",{id:"async-database-loader"},"Async Database Loader"),(0,o.kt)("p",null,"Template loaders can implement ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source_async"),". When a template is rendered by awaiting\n",(0,o.kt)("inlineCode",{parentName:"p"},"render_async")," instead of calling ",(0,o.kt)("inlineCode",{parentName:"p"},"render"),", ",(0,o.kt)("inlineCode",{parentName:"p"},"{% render %}")," and ",(0,o.kt)("inlineCode",{parentName:"p"},"{% include %}")," tags will use\n",(0,o.kt)("inlineCode",{parentName:"p"},"get_template_async")," of the bound ",(0,o.kt)("inlineCode",{parentName:"p"},"Environment"),", which delegates to ",(0,o.kt)("inlineCode",{parentName:"p"},"get_source_async")," of the\nconfigured loader."),(0,o.kt)("p",null,"For example, ",(0,o.kt)("inlineCode",{parentName:"p"},"AsyncDatabaseLoader")," will load templates from a PostgreSQL database using\n",(0,o.kt)("a",{parentName:"p",href:"https://github.com/MagicStack/asyncpg"},"asyncpg"),"."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'import datetime\nimport functools\n\nimport asyncpg\n\nfrom liquid import Environment\nfrom liquid.exceptions import TemplateNotFound\nfrom liquid.loaders import BaseLoader\nfrom liquid.loaders import TemplateSource\n\n\nclass AsyncDatabaseLoader(BaseLoader):\n    def __init__(self, pool: asyncpg.Pool) -> None:\n        self.pool = pool\n\n    def get_source(self, env: Environment, template_name: str) -> TemplateSource:\n        raise NotImplementedError("async only loader")\n\n    async def _is_up_to_date(self, name: str, updated: datetime.datetime) -> bool:\n        async with self.pool.acquire() as connection:\n            return updated == await connection.fetchval(\n                "SELECT updated FROM templates WHERE name = $1", name\n            )\n\n    async def get_source_async(\n        self, env: Environment, template_name: str\n    ) -> TemplateSource:\n        async with self.pool.acquire() as connection:\n            source = await connection.fetchrow(\n                "SELECT source, updated FROM templates WHERE name = $1", template_name\n            )\n\n        if not source:\n            raise TemplateNotFound(template_name)\n\n        return TemplateSource(\n            source=source["source"],\n            filename=template_name,\n            uptodate=functools.partial(\n                self._is_up_to_date, name=template_name, updated=source["updated"]\n            ),\n        )\n')),(0,o.kt)("h2",{id:"file-extension-loader"},"File Extension Loader"),(0,o.kt)("p",null,"This example extends ",(0,o.kt)("inlineCode",{parentName:"p"},"FileSystemLoader")," to automatically append a file extension if one is\nmissing."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-python"},'from pathlib import Path\n\nfrom typing import Union\nfrom typing import Iterable\n\nfrom liquid.loaders import FileSystemLoader\n\n\nclass FileExtensionLoader(FileSystemLoader):\n    """A file system loader that adds a file name extension if one is missing."""\n\n    def __init__(\n        self,\n        search_path: Union[str, Path, Iterable[Union[str, Path]]],\n        encoding: str = "utf-8",\n        ext: str = ".liquid",\n    ):\n        super().__init__(search_path, encoding=encoding)\n        self.ext = ext\n\n    def resolve_path(self, template_name: str) -> Path:\n        template_path = Path(template_name)\n\n        if not template_path.suffix:\n            template_path = template_path.with_suffix(self.ext)\n\n        # Don\'t allow "../" to escape the search path.\n        if os.path.pardir in template_path.parts:\n            raise TemplateNotFound(template_name)\n\n        for path in self.search_path:\n            source_path = path.joinpath(template_path)\n\n            if not source_path.exists():\n                continue\n            return source_path\n        raise TemplateNotFound(template_name)\n')))}c.isMDXComponent=!0}}]);