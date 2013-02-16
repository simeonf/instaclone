from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack

import os
from instaclone import util
from filters import registry, convert_image

# configuration
import config
app = config.app
    
@app.route('/')
def front_page():
    db = util.get_db()
    db.execute("""select * from instaclone_images
                               order by id desc limit 5""")
    rows = db.fetchall()
    return render_template('front_page.html', rows=rows, front_page=True)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/image/<pk>', methods=['POST', 'GET'])
def pic(pk):
    db = util.get_db()
    db.execute('select * from instaclone_images where id=%s', [pk])
    image = db.fetchone()
    # create filtered image if requested
    if request.method == 'POST':
        filter_name = request.form.get('filter')
        if filter_name in registry:
            im = util.Image(image)
            # Get current file
            image_path = im.get_relative_path()
            # Get new unique filename
            new_filename = util.new_filename(image_path)
            # copy old to new by way of selected filter
            convert_image(image_path, new_filename, filter_name)
            # and insert into the db
            pk = util.insert_image(os.path.basename(new_filename),
                                   "%s (%s)" % (im.name, filter_name),
                                   parent=im.parent_id or im.id,
                                   mv=False
                                   )
            return redirect(url_for('pic', pk=pk))
    sql = 'select * from instaclone_images where parent_id=%s'
    db.execute(sql, [pk])
    related = db.fetchall()
    return render_template('image.html', image=image,
                           related=related, filters=registry.keys())

@app.route('/like/<pk>', methods=['POST'])
def like(pk):
    db = util.get_db()
    db.execute('select * from instaclone_images where id=%s',
                       [pk])
    image = db.fetchone()
    if not image:
        abort(404)
    curs = db.execute("""insert into instaclone_likes(image)
                             values(%s)""",
                      [pk])
    return "1"

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    errors = []    
    if request.method == 'POST':
        # validate the form
        if 'image' not in request.files:
            errors.append('Please select a file to upload!')
        # process if valid
        else:
            pk = util.insert_image(request.files['image'],
                                   request.form.get('name'))
            return redirect(url_for('pic', pk=pk))
    else:
        return render_template('upload.html', errors=errors)

    
if __name__ == "__main__":
    util.config_templates(config.app)
    config.app.run()
