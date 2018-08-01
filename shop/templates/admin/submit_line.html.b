{% load i18n %}
<div class="submit-row" {% if is_popup %}style="overflow: auto;"{% endif %}>
{% if show_save %}<input type="submit" value="{% trans 'Save' %}" class="default" name="_save" {{ onclick_attrib }}/>{% endif %}
{% if show_delete_link %}<p class="deletelink-box"><a href="delete/" class="deletelink">{% trans "Delete" %}</a></p>{% endif %}
{% if show_save_as_new %}<input type="submit" value="{% trans 'Save as new' %}" name="_saveasnew" {{ onclick_attrib }}/>{%endif%}
{% if show_save_and_continue %}<input type="submit" value="{% trans 'Save and continue editing' %}" name="_continue" {{ onclick_attrib }}/>{% endif %}
</div>