""" Render views for logging in and out of the web interface """
from paste.httpheaders import WWW_AUTHENTICATE
from pyramid.httpexceptions import HTTPForbidden, HTTPFound, HTTPBadRequest
from pyramid.security import NO_PERMISSION_REQUIRED, remember, forget
from pyramid.view import view_config
from pyramid_duh import argify

from pypicloud.route import Root


@view_config(context=Root, name='login', request_method='GET',
             permission=NO_PERMISSION_REQUIRED, subpath=(),
             renderer='login.jinja2')
@view_config(context=HTTPForbidden, permission=NO_PERMISSION_REQUIRED,
             renderer='login.jinja2')
def get_login_page(request):
    """ Catch login and redirect to login wall """
    login_url = request.app_url('login')
    if request.userid is not None:
        # User is logged in and fetching /login, so redirect to /
        if request.url == login_url:
            return HTTPFound(location=request.app_url())
        else:
            # If user is not authorized, hide the page
            request.response.status_code = 404
            return request.response
    if request.url != login_url:
        # If pip requested a protected package and it's not authed, prompt for
        # credentials
        if (request.path.startswith('/simple') or
                request.path.startswith('/pypi')):
            request.response.status_code = 401
            realm = WWW_AUTHENTICATE.tuples('Basic realm="%s"' %
                                            request.registry.realm)
            request.response.headers.update(realm)
            return request.response
        else:
            # If user is not logged in, hide the page
            request.response.status_code = 404
            return request.response
    return {}


@view_config(context=Root, name='login', request_method='POST', subpath=(),
             renderer='json', permission=NO_PERMISSION_REQUIRED)
@argify
def do_login(request, username, password):
    """ Check credentials and log in """
    if request.access.verify_user(username, password):
        request.response.headers.extend(remember(request, username))
        return {
            'next': request.app_url(),
        }
    else:
        return HTTPForbidden()


@view_config(context=Root, name='login', request_method='PUT', subpath=(),
             renderer='json', permission=NO_PERMISSION_REQUIRED)
@argify
def register(request, username, password):
    """ Check credentials and log in """
    if not request.access.allow_register():
        return HTTPForbidden()
    if request.access.user_data(username) is not None:
        return HTTPBadRequest()
    request.access.register(username, password)
    return request.response


@view_config(context=Root, name='logout', subpath=())
def logout(request):
    """ Delete the user session """
    request.response.headers.extend(forget(request))
    return HTTPFound(location=request.app_url())
