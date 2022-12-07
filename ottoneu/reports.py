from jinja2 import Template
import codecs
import os
from slugify import slugify
from valuation import valuation

def main():
    report_generator(report_type='cut_or_keep')


# def daily_roster_report(roster):
#     # curpath = os.path.abspath(os.curdir)

#     with open(os.path.join(os.getenv("HUGO_TEMPLATES"),'daily_roster.md'), 'r') as file:
#         template = Template(file.read(), trim_blocks=True)
#     rendered_file = template.render(data=roster)

#     output_file = codecs.open(os.path.join(os.getenv("HUGO_CONTENT_PATH"),f"roster-{slugify(roster['team_name'])}-{roster['date']}.md"), "a", "utf-8")

#     output_file.write(rendered_file)
#     output_file.close()

# def cut_or_keep(cuts):

#     cuts = valuation()

#     with open(os.path.join(os.getenv("HUGO_TEMPLATES"),'cut_or_keep.md'), 'r') as file:
#         template = Template(file.read(), trim_blocks=True)
#     rendered_file = template.render(data=cuts)

#     output_file = codecs.open(os.path.join(os.getenv("HUGO_CONTENT_PATH"),f"cut-or-keep-{slugify(cuts['team_name'])}-{cuts['date']}.md"), "a", "utf-8")

#     output_file.write(rendered_file)
#     output_file.close()

def report_generator(report_type):
    if report_type == 'cut_or_keep':
        data = valuation()

     
    with open(os.path.join(os.getenv("HUGO_TEMPLATES"),f'{report_type}.md'), 'r') as file:
        template = Template(file.read(), trim_blocks=True)
    rendered_file = template.render(data=data)

    # TODO: Delete file if already exists
    file_name = os.path.join(os.getenv("HUGO_CONTENT_PATH"),f"{slugify(report_type)}-{slugify(data['team_name'])}-{data['date']}.md")
    
    if os.path.exists(file_name):
        os.remove(file_name)

    output_file = codecs.open(file_name, "a", "utf-8")

    output_file.write(rendered_file)
    output_file.close()

if __name__ == '__main__':
    main()