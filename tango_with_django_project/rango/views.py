from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import UserForm, UserProfileForm
from rango.forms import CategoryForm, PageForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime

def encode_url(str):
        return str.replace(' ', '_')

def decode_url(str):
        return str.replace('_', ' ')

def index(request):
        context = RequestContext(request)

        category_list = Category.objects.order_by('-likes')[:5]
        context_dict = {'categories': category_list}

        for category in category_list:
                category.url = encode_url(category.name)

        page_list = Page.objects.order_by('-views')[:5]
        context_dict['pages'] = page_list

        #### NEW CODE ####
        if request.session.get('last_visit'):
                # The session has a value for the last visit
                last_visit_time = request.session.get('last_visit')
                visits = request.session.get('visits', 0)

                if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
                        request.session['visits'] = visits + 1
        else:
                # The get returns None, and the session does not have a value for the last visit.
                request.session['last_visit'] = str(datetime.now())
                request.session['visits'] = 1
        #### END NEW CODE ####

        # Render and return the rendered response back to the user.
        return render_to_response('rango/index.html', context_dict, context)

def about(request):
        # Request the contex.
        context = RequestContext(request)

        # If the visits session varible exists, take it and use it.
        # If it doesn't, we haven't visited the site so set the count to zero.
        if request.session['visits']:
                count = request.session['visits']
        else:
                count = 0

        # Return and render the response, ensuring the count is passed to the template engine.
        return render_to_response('rango/about.html', {'visit_count': count}, context)

def category(request, category_name_url):
        # Request our context
        context = RequestContext(request)

        # Change underscores in the category name to spaces.
        # URL's don't handle spaces well, so we encode them as underscores.
        category_name = decode_url(category_name_url)

        # Build up the dictionary we will use as out template context dictionary.
        context_dict = {'category_name': category_name, 'category_name_url': category_name_url}

        try:
                # Find the category with the given name.
                # Raises an exception if the category doesn't exist.
                # We also do a case insensitive match.
                category_model = Category.objects.get(name__iexact=category_name)

                # Retrieve all the associated pages.
                # Note that filter returns >= 1 model instance.
                pages = Page.objects.filter(category=category_model)

                # Adds our results list to the template context under name pages.
                context_dict['pages'] = pages
        except Category.DoesNotExist:
                # We get here if the category does not exist.
                # Will trigger the template to display the 'no category' message.
                pass

        # Go render the response and return it to the client.
        return render_to_response('rango/category.html', context_dict, context)

@login_required
def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # No form passed - ignore and keep going.
            pass
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('rango/add_category.html', {'form': form}, context)

@login_required
def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            cat = Category.objects.get(name=category_name)
            page.category = cat

            # Also, create a default value for the number of views.
            page.views = 0

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return category(request, category_name)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html',
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form},
             context)

def register(request):
        # Request the context.
        context = RequestContext(request)

        # Boolean telling us whether registration was successful or not.
        # Initially False; presume it was a failure until proven otherwise!
        registered = False

        # If HTTP POST, we wish to process form data and create an account.
        if request.method == 'POST':
                # Grab raw form data - making use of both FormModels.
                user_form = UserForm(data=request.POST)
                profile_form = UserProfileForm(data=request.POST)

                # Two valid forms?
                if user_form.is_valid() and profile_form.is_valid():
                        # Save the user's form data. That one is easy.
                        user = user_form.save()

                        # Now a user account exists, we hash the password with the set_password() method.
                        # Then we can update the account with .save().
                        user.set_password(user.password)
                        user.save()

                        # Now we can sort out the UserProfile instance.
                        # We'll be setting values for the instance ourselves, so commit=False prevents Django from saving the instance automatically.
                        profile = profile_form.save(commit=False)
                        profile.user = user

                        # Profile picture supplied? If so, we put it in the new UserProfile.
                        if 'picture' in request.FILES:
                                profile.picture = request.FILES['picture']

                        # Now we save the model instance!
                        profile.save()

                        # We can say registration was successful.
                        registered = True

                # Invalid form(s) - just print errors to the terminal.
                else:
                        print user_form.errors, profile_form.errors

        # Not a HTTP POST, so we render the two ModelForms to allow a user to input their data.
        else:
                user_form = UserForm()
                profile_form = UserProfileForm()

        # Render and return!
        return render_to_response(
                'rango/register.html',
                {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
                context)

def user_login(request):
        # Obtain our request's context.
        context = RequestContext(request)

        # If HTTP POST, pull out form data and process it.
        if request.method == 'POST':
                username = request.POST['username']
                password = request.POST['password']

                # Attempt to log the user in with the supplied credentials.
                # A User object is returned if correct - None if not.
                user = authenticate(username=username, password=password)

                # A valid user logged in?
                if user is not None:
                        # Check if the account is active (can be used).
                        # If so, log the user in and redirect them to the homepage.
                        if user.is_active:
                                login(request, user)
                                return HttpResponseRedirect('/rango/')
                        # The account is inactive; tell by adding variable to the template context.
                        else:
                                return render_to_response('rango/login.html', {'disabled_account': True}, context)
                # Invalid login details supplied!
                else:
                        print "Invalid login details: {0}, {1}".format(username, password)
                        return render_to_response('rango/login.html', {'bad_details': True}, context)

        # Not a HTTP POST - most likely a HTTP GET. In this case, we render the login form for the user.
        else:
                return render_to_response('rango/login.html', {}, context)

@login_required
def restricted(request):
        context = RequestContext(request)
        return render_to_response('rango/restricted.html', {}, context)

# Only allow logged in users to logout - add the @login_required decorator!
@login_required
def user_logout(request):
        # Get the request's context
        context = RequestContext(request)

        # As we can assume the user is logged in, we can just log them out.
        logout(request)

        # Take the user back to the homepage.
        return HttpResponseRedirect('/rango/')