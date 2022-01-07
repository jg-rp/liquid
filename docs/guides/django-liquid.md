# Django Liquid

A [Django template backend](https://docs.djangoproject.com/en/4.0/topics/templates/) for Python Liquid.

## Install

Install Django Liquid using [Pipenv](https://pipenv.pypa.io/en/latest/):

```shell
$ pipenv install django-liquid
```

Or [pip](https://pip.pypa.io/en/stable/getting-started/):

```shell
$ python -m pip install -U django-liquid
```

## Configure

Configure Django Liquid with the [`TEMPLATES`](https://docs.djangoproject.com/en/4.0/topics/templates/#configuration) setting in your `settings.py` file, using `django_liquid.liquid.liquid` for the `BACKEND` setting. This example keeps the default Django template backend configuration, as created with [startproject](https://docs.djangoproject.com/en/4.0/ref/django-admin/#django-admin-startproject), and adds configuration for a Liquid template backend.

```python title="settings.py"
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django_liquid.liquid.Liquid',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {},
    },
]
```

When `APP_DIRS` is `True`, Liquid will look for templates in the `liquid` subdirectory of installed applications. `OPTIONS` are passed to the [liquid.Environment()](/api/Environment) constructor. The default environment is configured as follows.

- `autoescape`: `True`
- `loader`: a `FileSystemLoader` configured for `DIRS` and `APP_DIRS`
- `undefined`: `DebugUndefined` if `settings.DEBUG` else `Undefined`

## Render

Render Liquid templates from your app views just like any other Django template backend.

```python title="views.py"
from django.shortcuts import render

def index(request):
    context = {"greeting": "hello"}
    return render(request, 'myapp/index.html', context)
```

If you've got multiple template engines configured, like in the example above, Django will use the first engine and template it finds matching the given template name. You can force Django to use a specific template engine with the `using` argument to `render`.

```python title="views.py"
from django.shortcuts import render

def index(request):
    context = {"greeting": "hello"}
    return render(request, 'myapp/index.html', context, using='liquid')
```

## Environment Factory

You can configure your [liquid.Environment](/api/Environment) with additional tags or filters by setting the `environment` template backend option to the name of an `Environment` factory function. Lets say you want to register the [json](http://localhost:3000/liquid/extra/introduction) filter from [python-liquid-extra](/extra/introduction). If the following is saved as `myproject/liquid.py`:

```python title="myproject/liquid.py"
from liquid import Environment
from liquid_extra import filters

def environment(**options):
    env = Environment(**options)
    env.add_filter("json", filters.JSON())
    # Register more filters or tags here.
    return env
```

Then tell Django to use your environment factory function like this.

```python title="settings.py"
TEMPLATES = [
    {
        'BACKEND': 'django_liquid.liquid.Liquid',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'myproject.liquid.environment'
        },
    },
]
```
