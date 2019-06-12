from app import app, db
from app import update as upd
from flask import jsonify, request
from app.models import Research, ResearchModule, ConductedResearch, ResearchKeyword


@app.route('/')
def index():
    return "pitcher"


@app.route('/ml/api/v1.0/update/<int:res_id>', methods=['GET'])
def update(res_id):
    from datetime import datetime

    current_research = Research.query.filter_by(id=res_id).first()
    keywords = ResearchKeyword.query.filter_by(
        researchId=res_id).all()
    modules = ResearchModule.query.filter_by(
        researchId=res_id).all()

    keywords = ' '.join([k.keyword for k in keywords])
    modules = [m.module for m in modules]

    if current_research is None:
        return jsonify({'result': 'No such research'})
    
    itter = ConductedResearch()
    itter.date = datetime.now()
    itter.researchId = res_id
    
    if 'play_store' in modules:
        if current_research.appId is None:
            itter.play_store.append(upd.update_play_store(itter, current_research.algos, 
            app_id=current_research.appId))
        
        else:
            itter.play_store.append(upd.update_play_store(itter, current_research.algos, 
            app_name=current_research.appName,
            app_dev=current_research.appDev))
        
        db.session.commit()
        print('Play store updated')

    if 'twitter' in modules:
        itter.twitter.append(upd.update_twitter(itter, current_research.algos, keywords))
        db.session.commit()
        print('twitter updated')
    
    if 'news' in modules:
        itter.news.append(upd.update_news(itter, current_research.algos, keywords, 'ru'))
        db.session.commit()
        print('news updated')
    
    if 'search' in modules:
        upd.update_trends(current_research.id, current_research.algos, keywords, 'ru', 'UA')
        print('search updated')

    try:
        db.session.add(itter)
        db.session.commit()
    except Exception as e:
        print(e)

    return jsonify({
            "done": True,
            "message": "updated"
        })
