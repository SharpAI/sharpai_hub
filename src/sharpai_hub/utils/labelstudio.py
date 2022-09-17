import requests
import logging

TaskTemplate = {'title': 'Screen Monitoring dataset', 
                'description': '', 
                'label_config': '<View> \n<Image name="image" value="$image"/>\n<Choices name="choice" toName="image">\n<Choice value="coding"/><Choice value="study"/><Choice value="gaming"/></Choices>\n</View>', 
                'expert_instruction': '', 'show_instruction': False, 'show_skip_button': True, 'enable_empty_annotation': True, 'show_annotation_history': True, 
                'organization': 1, 'color': '#FFFFFF', 'maximum_annotations': 1, 'is_published': True, 'model_version': '', 'is_draft': False, 
                'min_annotations_to_start_training': 0, 
                'start_training_on_annotation_update': False, 'show_collab_predictions': True,
                'sampling': 'Sequential sampling', 'show_ground_truth_first': True, 
                'show_overlap_first': True, 'overlap_cohort_percentage': 100, 'task_data_login': None, 'task_data_password': None, 
                'control_weights': {'label': {'overall': 1.0, 'type': 'RectangleLabels', 'labels': {'person': 1.0, 'gun': 1.0, 'long gun': 1.0,'car': 1.0,'bus': 1.0,'truck': 1.0,'FP': 1.0}}}, 
                'evaluate_predictions_automatically': False, 
                'config_has_control_tags': True}


def check_label_studio_access(server_url,token):
    auth_header = {'Authorization' : 'Token {}'.format(token)}
    project_url = "{}/api/projects/".format(server_url)
    response = requests.get(project_url,headers=auth_header)
    print(response)
    if response.ok:
        return True
    return False

def create_labelstudio_image_classification_project(server_url,token,project_name,classes):
    logging.debug('Need create project {}'.format(project_name))
    TaskTemplate['title'] = project_name
    auth_header = {'Authorization' : f'Token {token}'}
    project_url = f"{server_url}/api/projects/"
    
    label_config = '<View> \n<Image name="image" value="$image"/>\n<Choices name="choice" toName="image">\n'
    
    for cls in classes:
        label_config+=f'<Choice value="{cls}"/>'
    label_config+='</Choices>\n</View>'
    
    TaskTemplate['label_config'] = label_config
    response = requests.post(project_url, json=TaskTemplate,  headers=auth_header)
    if response.ok:
        current_project = response.json()
        logging.debug(response.json())
        return response.json()
    logging.error('Failed to create project')
    return None

