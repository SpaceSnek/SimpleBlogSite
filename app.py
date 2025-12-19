import time
import os
import markdown2
from datetime import datetime
from flask import Flask, render_template, g, request, session, redirect, url_for
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('secret_key')

@app.route('/set-theme/<theme>')
def set_theme(theme):
    session['theme'] = theme
    return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_globals():
    return {
        'current_theme': session.get('theme', 'dark'),
        'load_time': lambda: f"{time.time() - g.start:.3f}"
    }

@app.before_request
def start_timer():
    g.start = time.time()

def get_grouped_posts():
    posts_dir = os.path.join(app.root_path, 'posts') 
    if not os.path.exists(posts_dir):
        return {}

    filenames = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md')], reverse=True)
    grouped = {}
    
    for f in filenames:
        date_str = f.replace('.md', '')
        try:
            month_header = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %Y')
            grouped.setdefault(month_header, []).append(date_str)
        except ValueError:
            continue
    return grouped

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog_index():
    return render_template('blog_index.html', grouped_posts=get_grouped_posts())

@app.route('/blog/<post_name>')
def render_post(post_name):
    # Updated path to the new root-level posts folder
    safe_name = secure_filename(post_name)
    path = os.path.join(app.root_path, 'posts', f'{safe_name}.md')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html_content = markdown2.markdown(f.read(), extras=["fenced-code-blocks", "tables", "break-on-newline"])
        return render_template('post_wrapper.html', content=html_content, title=post_name)
    except FileNotFoundError:
        return "Post not found", 404

if __name__ == '__main__':
    app.run(debug=True)