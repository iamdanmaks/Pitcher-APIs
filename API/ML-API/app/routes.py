from app import app, db
from app.update import update_play_store
from flask import jsonify, request
from app.models import Research, ResearchModule, ConductedResearch, ResearchKeyword


@app.route('/')
def index():
    return "pitcher"


@app.route('/ml/api/v1.0/update/<int:res_id>', methods=['POST'])
def update(res_id):
    from datetime import datetime

    current_research = Research.query.filter_by(id=res_id).first()
    modules = ResearchModule.query.filter_by(
        researchId=res_id).options(load_only('module')).all()

    if current_research is None:
        return jsonify({'result': 'No such research'})
    
    itter = ConductedResearch()
    itter.date = datetime.now()
    
    if 'Play Store' in modules:
        if current_research.appId is None:
            itter.play_store.append(update.update_play_store(itter, request.args.get('pl_clf'), 
            app_id=current_research.appId))
        
        else:
            itter.play_store.append(update.update_play_store(itter, request.args.get('pl_clf'), 
            app_name=current_research.appName,
            app_dev=current_research.appDev))

    if 'Twitter' in modules:
        itter.twitter.append()

    current_research.conducted.append(itter)
    
    db.session.add(itter)
    db.session.commit()

    return jsonify({'done': True, 'message': 'updated'})
