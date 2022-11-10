from flask import request, render_template, url_for, send_file, redirect, flash, session
from portfolio_builder.app import app
from portfolio_builder.app import mongo, users_accounts_col, portfolio_details_col
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/')
def home():
    if session.get('logged_in'):
        session.pop('logged_in', None)
        return render_template('index.html', login_success=1, logout=1)
    elif session.get('logged_out'):
        session.pop('logged_out', None)
        return render_template('index.html', logout_success=1, login=1)
    elif session.get('username'):
        return render_template('index.html', logout=1)
    elif session.get('no_account'):
        return render_template('index.html', login=1, no_account=1)
    else:
        return render_template('index.html', login=1)


@app.route('/add_portfolio_details')
def add_portfolio_details():
    return render_template('enter-portfolio-details.html')


@app.route("/dashboard")
def dashboard():
    if session.get('username'):
        portfolio_details = portfolio_details_col.find_one({'username': session['username']})
        users_details = users_accounts_col.find_one({'username': session['username']})
        updated_account = 0
        updated_password = 0
        updated_username_exists = 0
        updated_email_exists = 0
        if session.get('update_account'):
            updated_account = 1
            session.pop('update_account', None)
        if session.get('update_password'):
            updated_password = 1
            session.pop('update_password', None)
        if session.get('update_username_exists'):
            updated_username_exists = session['update_username_exists']
            session.pop('update_username_exists', None)
        if session.get('update_email_exists'):
            updated_email_exists = session['update_email_exists']
            session.pop('update_email_exists', None)
        return render_template("dashboard.html", users_details=users_details, portfolio_details=portfolio_details, updated_account=updated_account, updated_password=updated_password, updated_username_exists=updated_username_exists, updated_email_exists=updated_email_exists)
    else:
        session['dashboard_route'] = 'True'
        return redirect(url_for('login'))


@app.route('/login')
def login():
    if session.get('username'):
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/verify_login', methods=['POST', 'GET'])
def verify_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_accounts_col.find_one({'email': email})
        if user is not None:
            if check_password_hash(user['password'], password):
                session['username'] = user['username']
                if session.get('template_id'):
                    template_id = session['template_id']
                    session.pop('template_id', None)
                    return redirect(url_for('use_template', template_id=template_id))
                if session.get('dashboard_route'):
                    session.pop('dashboard_route', None)
                    return redirect(url_for('dashboard'))
                session['logged_in'] = 1
                return redirect(url_for('home'))
            else:
                return render_template('login.html', login_failed=1)
        else:
            session['no_account'] = 1
            return redirect(url_for('home'))


@app.route('/create_account', methods=['POST', 'GET'])
def create_account():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_username_exists = users_accounts_col.find_one({'username': username})
        is_email_exists = users_accounts_col.find_one({'username': username})
        if is_username_exists:
            return render_template('create_account.html', username_exists=1)
        elif is_email_exists:
            return render_template('create_account.html', is_email_exists=1)
        else:
            users_accounts_col.insert_one({'firstname': firstname,
                                           'lastname': lastname,
                                           'username': username,
                                           'email': email,
                                           'password': generate_password_hash(password)})
            return render_template('login.html', account=1)

    return render_template('create_account.html')


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        passkey = request.form['passkey']
        if passkey == '18920821':
            return "Admin Login successful: {}".format(passkey)
        else:
            return 'Restricted. '
    return render_template('admin.html')


@app.route('/<template_id>/use_template', methods=['POST', 'GET'])
def use_template(template_id):
    if session.get('username') is None:
        session['template_id'] = template_id
        return redirect(url_for('login'))
    is_portfolio_exist = portfolio_details_col.find_one({'username': session['username']})
    if is_portfolio_exist:
        return 'Already Portfolio Created. Only one portfolio per username'
    interests = ['Competitive Programming', 'Machine Learning', 'Deep Learning', 'Data Science', 'Web Development', 'Application Development', 'Blogging', 'Content Writing', 'Software Development', 'Graphic Designing']
    interests_len = len(interests)
    return render_template('enter-portfolio-details.html', template_id=template_id, user_name=session['username'], interests=interests, interests_len=interests_len)


@app.route('/read_portfolio_details', methods=['POST', 'GET'])
def read_portfolio_details():
    if request.method == 'POST':
        template_id = request.form['template_id']
        name = request.form['name']
        gender = request.form['gender']
        current_role = request.form['current_role']

        # contacts
        email = request.form['email']
        mobile_no = request.form['mobile_no']
        city = request.form['city']

        # social Media Links
        linkedin = request.form['linkedin']
        github = request.form['github']
        instagram = request.form['instagram']
        twitter = request.form['twitter']

        # resume
        resume = request.files['resume']
        mongo.save_file(resume.filename, resume)

        # user image
        user_img = request.files['user_img']
        mongo.save_file(user_img.filename, user_img)

        # about you
        about_you = request.form['about_you']

        # education
        school_name = request.form.getlist('Schoolname[]')
        major = request.form.getlist('Major[]')
        degree = request.form.getlist('Degree[]')
        start_date = request.form.getlist('StartDate[]')
        end_date = request.form.getlist('EndDate[]')
        gpa = request.form.getlist('GPA[]')

        # Experience
        company_name = request.form.getlist('Companyname[]')
        role = request.form.getlist('Role[]')
        exp_start_date = request.form.getlist('ExpStartDate[]')
        exp_last_date = request.form.getlist('ExpLastDate[]')
        current_job_check = request.form.getlist('CurrentJobCheck[]')
        desc_exp = request.form.getlist('DescExp[]')

        # projects
        project_name = request.form.getlist('Projectname[]')
        domain = request.form.getlist('Domain[]')
        project_link = request.form.getlist('ProjectLink[]')
        desc_project = request.form.getlist('DescProject[]')

        # skills
        skills = request.form.getlist('skills[]')
        skills_list = []
        skills_scores = []
        for each_skill in skills:
            lis = each_skill.split(',')
            skills_list.append(lis[0])
            skills_scores.append(int(lis[1]))

        # interests
        interests = request.form.getlist('interests_list[]')

        portfolio_details_dict = {
            'username': session['username'],
            'template_id': template_id,
            'name': name,
            'gender': gender,
            'current_role': current_role,
            'email': email,
            'mobile_no': mobile_no,
            'city':city,
            'linkedin': linkedin,
            'github': github,
            'instagram': instagram,
            'twitter': twitter,
            'resume_filename': resume.filename,
            'user_img_filename': user_img.filename,
            'about_you': about_you,
            'school_name': school_name,
            'major': major,
            'degree': degree,
            'start_date': start_date,
            'end_date': end_date,
            'gpa': gpa,
            'company_name': company_name,
            'role': role,
            'exp_start_date': exp_start_date,
            'exp_last_date': exp_last_date,
            'current_job_link': current_job_check,
            'desc_exp': desc_exp,
            'project_name': project_name,
            'domain': domain,
            'project_link': project_link,
            'desc_project': desc_project,
            'skills_list': skills_list,
            'skills_scores': skills_scores,
            'interests': interests
        }

        portfolio_details_col.insert_one(portfolio_details_dict)
        return render_template('portfolio_link.html', user_name=session['username'])


@app.route('/<user_name>')
def portfolio(user_name):
    print(user_name)
    templates_list = ['templates_list/template1.html', 'templates_list/template2.html']
    portfolio_details = portfolio_details_col.find_one({'username': user_name})
    if portfolio_details:
        session['url_username'] = user_name
        template = int(portfolio_details['template_id'])-1
        edu_len = len(portfolio_details['school_name'])
        exp_len = len(portfolio_details['company_name'])
        skills_len = len(portfolio_details['skills_list'])
        project_len = len(portfolio_details['project_name'])
        interests_len = len(portfolio_details['interests'])
        interests_icons = ['bi bi-code-slash',
                           'bi bi-gear',
                           'bi bi-cpu',
                           'bi bi-diagram-3',
                           'ti-desktop',
                           'ti-android',
                           'ti-wordpress',
                           'ti-pencil-alt2',
                           'bi bi-code-square',
                           'bi bi-brush'
                           ]
        interests = ['Competitive Programming',
                     'Machine Learning',
                     'Deep Learning',
                     'Data Science',
                     'Web Development',
                     'Application Development',
                     'Blogging',
                     'Content Writing',
                     'Software Development',
                     'Graphic Designing'
                     ]
        interests_icons_user = []
        interests_user = []
        for i in portfolio_details['interests']:
            interests_user.append(interests[int(i)])
            interests_icons_user.append(interests_icons[int(i)])
        contact_form_send = 'False'
        if session.get('contact_email_send'):
            contact_form_send = session['contact_email_send']
            session.pop('contact_email_send', None)
        print(portfolio_details['skills_scores'])
        print(portfolio_details['skills_list'],skills_len)
        return render_template(templates_list[template],
                               portfolio_details=portfolio_details,
                               edu_len=edu_len,
                               exp_len=exp_len,
                               skills_len=skills_len,
                               project_len=project_len,
                               interests_len=interests_len,
                               interests_icons_user=interests_icons_user,
                               interests_user=interests_user,
                               contact_from_send=contact_form_send
                               )
    else:
        return render_template('404.html')


@app.route('/update-portfolio', methods=['POST', 'GET'])
def update_portfolio():
    if session.get('username'):
        portfolio_details = portfolio_details_col.find_one({'username': session['username']})
        if portfolio_details:
            edu_len = len(portfolio_details['school_name'])
            exp_len = len(portfolio_details['company_name'])
            skills_len = len(portfolio_details['skills_list'])
            project_len = len(portfolio_details['project_name'])

            interests = ['Competitive Programming',
                         'Machine Learning',
                         'Deep Learning',
                         'Data Science',
                         'Web Development',
                         'Application Development',
                         'Blogging',
                         'Content Writing',
                         'Software Development',
                         'Graphic Designing'
                         ]
            interests_len = len(interests)
            return render_template('update-portfolio-details.html',
                                   template_id=int(portfolio_details['template_id']),
                                   user_name='Ajayvardhan',
                                   portfolio_details=portfolio_details,
                                   edu_len=edu_len,
                                   exp_len=exp_len,
                                   skills_len=skills_len,
                                   project_len=project_len,
                                   interests_len=interests_len,
                                   interests=interests
                                )
        else:
            return 'Create a portfolio first'
    return redirect(url_for('login'))


@app.route('/update_portfolio_details', methods=['POST', 'GET'])
def update_portfolio_details():
    if request.method == 'POST':
        template_id = request.form['template_id']
        user_name = request.form['user_name']
        name = request.form['name']
        gender = request.form['gender']
        current_role = request.form['current_role']

        # contacts
        email = request.form['email']
        mobile_no = request.form['mobile_no']
        city = request.form['city']

        # social Media Links
        linkedin = request.form['linkedin']
        github = request.form['github']
        instagram = request.form['instagram']
        twitter = request.form['twitter']

        # about you
        about_you = request.form['about_you']

        # education
        school_name = request.form.getlist('Schoolname[]')
        major = request.form.getlist('Major[]')
        degree = request.form.getlist('Degree[]')
        start_date = request.form.getlist('StartDate[]')
        end_date = request.form.getlist('EndDate[]')
        gpa = request.form.getlist('GPA[]')

        # Experience
        company_name = request.form.getlist('Companyname[]')
        role = request.form.getlist('Role[]')
        exp_start_date = request.form.getlist('ExpStartDate[]')
        exp_last_date = request.form.getlist('ExpLastDate[]')
        current_job_check = request.form.getlist('CurrentJobCheck[]')
        desc_exp = request.form.getlist('DescExp[]')

        # projects
        project_name = request.form.getlist('Projectname[]')
        domain = request.form.getlist('Domain[]')
        project_link = request.form.getlist('ProjectLink[]')
        desc_project = request.form.getlist('DescProject[]')

        # skills
        skills = request.form.getlist('skills[]')
        skills_list = []
        skills_scores = []
        for each_skill in skills:
            lis = each_skill.split(',')
            skills_list.append(lis[0])
            skills_scores.append(int(lis[1]))

        # interests
        interests = request.form.getlist('interests_list[]')

        portfolio_details_col.update_one({'username': user_name},
                                         {"$set": {
                                                    'template_id': template_id,
                                                    'name': name,
                                                    'gender': gender,
                                                    'current_role': current_role,
                                                    'email': email,
                                                    'mobile_no': mobile_no,
                                                    'city':city,
                                                    'linkedin': linkedin,
                                                    'github': github,
                                                    'instagram': instagram,
                                                    'twitter': twitter,
                                                    'about_you': about_you,
                                                    'school_name': school_name,
                                                    'major': major,
                                                    'degree': degree,
                                                    'start_date': start_date,
                                                    'end_date': end_date,
                                                    'gpa': gpa,
                                                    'company_name': company_name,
                                                    'role': role,
                                                    'exp_start_date': exp_start_date,
                                                    'exp_last_date': exp_last_date,
                                                    'current_job_link': current_job_check,
                                                    'desc_exp': desc_exp,
                                                    'project_name': project_name,
                                                    'domain': domain,
                                                    'project_link': project_link,
                                                    'desc_project': desc_project,
                                                    'skills_list': skills_list,
                                                    'skills_scores': skills_scores,
                                                    'interests': interests
                                                   }
                                         }
                                         )
        return 'updated'


@app.route('/update_account', methods=['POST', 'GET'])
def update_account():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        users_accounts_col.update_one({'username': email}, {"$set": {
                                                                        'firstname': firstname,
                                                                        'lastname': lastname,
                                                                        }
                                                               }
                                      )
        session['update_account'] = True
        return redirect(url_for('dashboard'))


@app.route('/update_password', methods=['POST', 'GET'])
def update_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        users_accounts_col.update_one({'email': email}, {"$set": {'password': generate_password_hash(new_password)} })
        session['update_password'] = True
        return redirect(url_for('dashboard'))


@app.route('/update_username', methods=['POST', 'GET'])
def update_username():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        is_username_exists = users_accounts_col.find_one({'username': username})
        if is_username_exists:
            session['update_username_exists'] = 1
            return redirect(url_for('dashboard'))
        users_accounts_col.update_one({'email': email}, {"$set": {'username': username}})
        portfolio_details_col.update_one({'username': session['username']}, {"$set": {"username": username}})
        session['username'] = username
        session['update_username_exists'] = 2
        return redirect(url_for('dashboard'))


@app.route('/update_email', methods=['POST', 'GET'])
def update_email():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        is_email_exists = users_accounts_col.find_one({'email': email})
        if is_email_exists:
            session['update_email_exists'] = 1
            return redirect(url_for('dashboard'))
        users_accounts_col.update_one({'username': username}, {"$set": {'email': email}})
        session['update_email_exists'] = 2
        return redirect(url_for('dashboard'))


@app.route('/delete_portfolio')
def delete_portfolio():
    return 'Building the route'


@app.route('/<template_id>/demo/portfolio', methods=['POST', 'GET'])
def demo_portfolio(template_id):
    # templates_list = ['templates_list/template1.html', 'templates_list/template2.html']
    # portfolio_details = portfolio_details_col.find_one({'template_id': str(template_id)})
    # template = int(portfolio_details['template_id']) - 1
    # return render_template(templates_list[template], portfolio_details=portfolio_details)
    return redirect(url_for('portfolio', user_name='Ajayvardhan'))


@app.route('/<username>/download_resume')
def download_resume(username):
    portfolio_details = portfolio_details_col.find_one({'username': username})
    file_name = portfolio_details['user_img_filename']
    print(file_name)
    response = mongo.send_file(file_name)
    print(response)
    return 'GOOD'


@app.route('/username')
def sess():
    if session.get('username'):
        return session['username']
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    if session.get('username'):
        session.pop('username', None)
        session['logged_out'] = 1
        return redirect(url_for('home'))
    else:
        return 'user needs to login first'


@app.route('/contact_form', methods=['post', 'get'])
def contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        session['contact_email_send'] = 'Message send Successfully!'
        return redirect(url_for('portfolio', user_name=session['url_username']))