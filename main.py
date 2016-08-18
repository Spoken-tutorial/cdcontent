"""Automatic cdcontent creator (all foss and languages)."""
import os
import zipfile
import calendar
import datetime

from jinja2 import Environment, FileSystemLoader
from config import (base_path, videos_path, zip_file_path, default_zip_file_path)

from models import (database, Language, TutorialResource)


def zipdir(src_path, dst_path, archive):
    for root, dirs, dir_files in os.walk(src_path):
        for dir_file in dir_files:
            archive.write(os.path.join(root, dir_file), os.path.join(dst_path, dir_file))


def get_foss_objects():
    """Get all foss which has tutorials."""
    foss_query = ("SELECT DISTINCT `creation_tutorialdetail`.`foss_id`, `creation_fosscategory`.`foss`"
                  " FROM `creation_tutorialresource` INNER JOIN `creation_tutorialdetail` ON "
                  "( `creation_tutorialresource`.`tutorial_detail_id` = `creation_tutorialdetail`.`id` ) "
                  "INNER JOIN `creation_fosscategory` ON "
                  "( `creation_tutorialdetail`.`foss_id` = `creation_fosscategory`.`id` ) WHERE "
                  "(`creation_tutorialresource`.`status` = 1 OR `creation_tutorialresource`.`status` = 2)"
                  " ORDER BY `creation_fosscategory`.`foss` ASC")
    return TutorialResource.raw(foss_query)


def get_foss_languages(foss_id):
    lang_query = ("SELECT DISTINCT `creation_tutorialresource`.`language_id`, `creation_language`.`name` FROM "
                  "`creation_tutorialresource` INNER JOIN `creation_tutorialdetail` ON "
                  "( `creation_tutorialresource`.`tutorial_detail_id` = `creation_tutorialdetail`.`id` ) "
                  "INNER JOIN `creation_language` ON "
                  "( `creation_tutorialresource`.`language_id` = `creation_language`.`id` ) WHERE "
                  "((`creation_tutorialresource`.`status` = 1 OR `creation_tutorialresource`.`status` = 2) AND "
                  "`creation_tutorialdetail`.`foss_id` = {}) ORDER BY `creation_language`.`name` ASC")
    lang_query = lang_query.format(foss_id)
    return TutorialResource.raw(lang_query)


def get_tutorial_resources_for_current_foss_lang(foss_id, lang_id):
    tr_query = ("SELECT `creation_tutorialresource`.`id`, `creation_tutorialresource`.`tutorial_detail_id`, "
                "`creation_tutorialresource`.`common_content_id`, `creation_tutorialresource`.`language_id`, "
                "`creation_tutorialresource`.`outline`, `creation_tutorialresource`.`outline_user_id`, "
                "`creation_tutorialresource`.`outline_status`, `creation_tutorialresource`.`script`, "
                "`creation_tutorialresource`.`script_user_id`, `creation_tutorialresource`.`script_status`, "
                "`creation_tutorialresource`.`timed_script`, `creation_tutorialresource`.`video`, "
                "`creation_tutorialresource`.`video_id`, `creation_tutorialresource`.`playlist_item_id`, "
                "`creation_tutorialresource`.`video_thumbnail_time`, `creation_tutorialresource`.`video_user_id`, "
                "`creation_tutorialresource`.`video_status`, `creation_tutorialresource`.`status`, "
                "`creation_tutorialresource`.`version`, `creation_tutorialresource`.`hit_count`, "
                "`creation_tutorialresource`.`created`, `creation_tutorialresource`.`updated` FROM "
                "`creation_tutorialresource` INNER JOIN `creation_tutorialdetail` ON "
                "( `creation_tutorialresource`.`tutorial_detail_id` = `creation_tutorialdetail`.`id` ) INNER JOIN "
                "`creation_language` ON ( `creation_tutorialresource`.`language_id` = `creation_language`.`id` ) "
                "WHERE ((`creation_tutorialresource`.`status` = 1 OR `creation_tutorialresource`.`status` = 2) "
                "AND `creation_tutorialdetail`.`foss_id` = {} AND `creation_tutorialresource`.`language_id` = {}) "
                "ORDER BY `creation_tutorialdetail`.`level_id` ASC, `creation_tutorialdetail`.`order` ASC, "
                "`creation_language`.`name` ASC")
    tr_query = tr_query.format(foss_id, lang_id)
    return TutorialResource.raw(tr_query)


def get_all_foss_details():
    all_foss_details = []

    for foss_obj in get_foss_objects():
        foss_dict = {'foss': foss_obj, 'langs': []}

        for language_obj in get_foss_languages(foss_obj.foss_id):
            foss_dict['langs'].append(language_obj)

        all_foss_details.append(foss_dict)

    return all_foss_details


def add_sheets(archive, foss_id, foss, lang):
    instruction_file = '{}/{}-Instruction-Sheet-{}.pdf'.format(foss_id,
                                                               foss.replace(' ', '-'),
                                                               lang)

    installation_file = '{}/{}-Installation-Sheet-{}.pdf'.format(foss_id,
                                                                 foss.replace(' ', '-'),
                                                                 lang)
    instruction_file_path = '{}{}'.format(videos_path, instruction_file)
    installation_file_path = '{}{}'.format(videos_path, installation_file)

    if os.path.isfile(instruction_file_path):
        new_file_path = 'spoken/videos/{}'.format(instruction_file)
        archive.write(instruction_file_path, new_file_path)

    if os.path.isfile(installation_file_path):
        new_file_path = 'spoken/videos/{}'.format(installation_file)
        archive.write(installation_file_path, new_file_path)


def get_sheet_link(sheet_type, foss_id, foss, lang):
    file_path = '{}{}/{}-{}-{}.pdf'.format(videos_path, foss_id,
                                           foss.replace(' ', '-'), sheet_type, lang)

    if lang != 'English':
        if os.path.isfile(file_path):
            file_path = '../{}-{}-{}.pdf'.format(foss.replace(' ', '-'), sheet_type, lang)
            return file_path

    file_path = '{}{}/{}-{}-English.pdf'.format(videos_path, foss_id, foss.replace(' ', '-'), sheet_type)
    if os.path.isfile(file_path):
            file_path = '../{}-{}-English.pdf'.format(foss.replace(' ', '-'), sheet_type)
            return file_path
    return False


def add_srt_file(archive, tr_rec, filepath, eng_flag, srt_files):
    ptr = filepath.rfind(".")
    filepath = filepath[:ptr] + '.srt'

    if os.path.isfile(videos_path + filepath):
        archive.write(videos_path + filepath, 'spoken/videos/' + filepath)

    if eng_flag:
        filepath = '{}/{}/{}-English.srt'.format(tr_rec.tutorial_detail.foss_id, tr_rec.tutorial_detail_id,
                                                 tr_rec.tutorial_detail.tutorial.replace(' ', '-'))

        if os.path.isfile(videos_path + filepath) and filepath not in srt_files:
            srt_files.add(filepath)
            archive.write(videos_path + filepath, 'spoken/videos/' + filepath)


def collect_common_files(tr_rec, common_files):
    common_files_path = '{}/{}/resources'.format(tr_rec.tutorial_detail.foss_id, tr_rec.tutorial_detail_id)

    if tr_rec.common_content.slide_status > 0:
        common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.slide))

    if tr_rec.common_content.assignment_status > 0 and tr_rec.common_content.assignment_status != 6:
        common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.assignment))

    if tr_rec.common_content.code_status > 0 and tr_rec.common_content.code_status != 6:
        common_files.add('{}/{}'.format(common_files_path, tr_rec.common_content.code))


def create_archive_file():
    zip_file_name = default_zip_file_path

    if os.path.isdir(zip_file_path):
        zip_file_name = zip_file_path

    zip_file_name = '{0}spoken_tutorials_{1}.zip'.format(zip_file_name,
                                                         calendar.timegm(datetime.datetime.utcnow().timetuple()))
    archive = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    archive.close()

    return zip_file_name


def open_archive_file(zip_file_name):
    return zipfile.ZipFile(zip_file_name, 'a', zipfile.ZIP_DEFLATED, allowZip64=True)


def get_zip_content(path):
    file_names = None
    try:
        zf = zipfile.ZipFile(path, 'r')
        file_names = zf.namelist()
        return file_names
    except Exception:
        return False


def get_srt_files(tr):
    data = ''
    k = tr.video.rfind(".")
    new_srtfile = tr.video[:k] + '.srt'

    if tr.language.name != 'English':
        srt_english = new_srtfile.replace(tr.language.name, 'English')
        filepath = '{}{}/{}/{}'.format(videos_path, tr.tutorial_detail.foss_id, tr.tutorial_detail_id,
                                       srt_english)
        if os.path.isfile(filepath):
            data += '<track kind="captions" src="./{}" srclang="en" label="English" />'.format(srt_english)

    filepath = '{}{}/{}/{}'.format(videos_path, tr.tutorial_detail.foss_id, tr.tutorial_detail_id, new_srtfile)

    if os.path.isfile(filepath):
        data += '<track kind="captions" src="./{}" srclang="en" label="{}" />'.format(new_srtfile, tr.language.name)
    return data


def get_review_status(key):
    status_list = ['Pending', 'Waiting for Admin Review', 'Waiting for Domain Review',
                   'Waiting for Quality Review', 'Accepted', 'Need Improvement', 'Not Required']
    return status_list[key]


def get_review_status_symbol(key):
    status_list = ['fa fa-1 fa-minus-circle review-pending-upload', 'fa fa-1 fa-check-circle review-admin-review',
                   'fa fa-1 fa-check-circle review-domain-review', 'fa fa-1 fa-check-circle review-quality-review',
                   'fa fa-1 fa-check-circle review-accepted', 'fa fa-1 fa-times-circle review-pending-upload',
                   'fa fa-1 fa-ban review-accepted']
    return status_list[key]


def get_show_video_context(tr_rec, tr_recs):
    ctx = {'tr_rec': tr_rec, 'tr_recs': list(tr_recs)}
    ctx['instr_link'] = get_sheet_link('Instruction-Sheet', tr_rec.tutorial_detail.foss_id,
                                       tr_rec.tutorial_detail.foss.foss, tr_rec.language.name)
    ctx['instl_link'] = get_sheet_link('Installation-Sheet', tr_rec.tutorial_detail.foss_id,
                                       tr_rec.tutorial_detail.foss.foss, tr_rec.language.name)
    common_files_path = '{}/{}/resources'.format(tr_rec.tutorial_detail.foss_id, tr_rec.tutorial_detail_id)
    ctx['code_files'] = get_zip_content('{}/{}'.format(common_files_path, tr_rec.common_content.code))
    ctx['slide_files'] = get_zip_content('{}/{}'.format(common_files_path, tr_rec.common_content.slide))
    ctx['srt_files'] = get_srt_files(tr_rec)
    ctx['assignment_status_symbol'] = get_review_status_symbol(tr_rec.common_content.assignment_status)
    ctx['assignment_status'] = get_review_status(tr_rec.common_content.assignment_status)
    ctx['code_status_symbol'] = get_review_status_symbol(tr_rec.common_content.code_status)
    ctx['code_status'] = get_review_status(tr_rec.common_content.code_status)
    ctx['slide_status_symbol'] = get_review_status_symbol(tr_rec.common_content.slide_status)
    ctx['slide_status'] = get_review_status(tr_rec.common_content.slide_status)

    return ctx


def convert_template_to_html_file(archive, filename, template_file, ctx):
    loader = FileSystemLoader('templates', followlinks=True)
    env = Environment(loader=loader)
    template = env.get_template(template_file)

    archive.writestr(filename, template.render(ctx).encode('utf-8'))


def add_common_files(archive, common_files):
    for filepath in common_files:
        if os.path.isfile(videos_path + filepath):
            archive.write(videos_path + filepath, 'spoken/videos/' + filepath)


def add_side_by_side_tutorials(archive, languages):
    languages.add('English')
    available_langs = set()

    for language in languages:
        filepath = '{}32/714/Side-by-Side-Method-{}.ogv'.format(videos_path, language)

        if os.path.isfile(filepath):
            available_langs.add(language)
            archive.write(filepath, 'spoken/videos/Side-by-Side-Method-{}.ogv'.format(language))

    return available_langs


def get_static_files():
    return {
        '/static/spoken/css/bootstrap.min.css': 'spoken/includes/css/bootstrap.min.css',
        '/static/spoken/css/font-awesome.min.css': 'spoken/includes/css/font-awesome.min.css',
        '/static/spoken/css/main.css': 'spoken/includes/css/main.css',
        '/static/spoken/css/video-js.min.css': 'spoken/includes/css/video-js.min.css',
        '/static/spoken/images/favicon.ico': 'spoken/includes/images/favicon.ico',
        '/static/spoken/images/logo.png': 'spoken/includes/images/logo.png',
        '/static/spoken/js/jquery-1.11.0.min.js': 'spoken/includes/js/jquery-1.11.0.min.js',
        '/static/spoken/js/bootstrap.min.js': 'spoken/includes/js/bootstrap.min.js',
        '/static/spoken/js/video.js': 'spoken/includes/js/video.js',
        '/static/spoken/images/thumb-even.png': 'spoken/includes/images/thumb-even.png',
        '/static/spoken/images/Basic.png': 'spoken/includes/images/Basic.png',
        '/static/spoken/images/Intermediate.png': 'spoken/includes/images/Intermediate.png',
        '/static/spoken/images/Advanced.png': 'spoken/includes/images/Advanced.png',
        '/static/cdcontent/templates/readme.txt': 'spoken/README.txt',
        '/static/cdcontent/templates/index.html': 'spoken/index.html'
    }


def add_static_files(archive):
    zipdir(base_path + '/static/spoken/fonts', 'spoken/includes/fonts/', archive)
    static_files = get_static_files()

    for key, value in static_files.items():
        filepath = '{}{}'.format(base_path, key)

        if os.path.isfile(filepath):
            archive.write(filepath, value)


def main():
    """Initiate cd content creation."""
    database.connect()

    # creating zip file
    zip_file_name = create_archive_file()
    archive = open_archive_file(zip_file_name)

    # collecting foss list
    languages = set()
    all_foss_details = get_all_foss_details()
    eng_rec = Language.get(Language.name == "English")

    for data in all_foss_details:
        foss_rec = data.get('foss')
        eng_flag = True
        srt_files = set()
        common_files = set()

        if len(filter(lambda lang: lang.name == eng_rec.name, data.get('langs'))):
            eng_flag = False

        for lang_obj in data.get('langs'):
            print 'Adding {} - {}'.format(foss_rec.foss, lang_obj.name)
            languages.add(lang_obj.name)
            tr_recs = get_tutorial_resources_for_current_foss_lang(foss_rec.foss_id, lang_obj.language_id)

            for rec in tr_recs:
                # collect common files
                collect_common_files(rec, common_files)
                ctx = get_show_video_context(rec, tr_recs)

                # archive = open_archive_file(zip_file_name)
                filepath = '{}/{}/{}'.format(foss_rec.foss_id, rec.tutorial_detail_id, rec.video)

                if os.path.isfile(videos_path + filepath):
                    archive.write(videos_path + filepath, 'spoken/videos/' + filepath)

                # add srt file to archive
                add_srt_file(archive, rec, filepath, eng_flag, srt_files)

                # add show video page
                filepath = 'spoken/videos/{}/{}/show-video-{}.html'.format(
                    rec.tutorial_detail.foss_id, rec.tutorial_detail_id, rec.language.name)
                convert_template_to_html_file(archive, filepath, "watch_tutorial.html", ctx)
                # archive.close()

            # archive = open_archive_file(zip_file_name)
            filepath = 'spoken/videos/' + str(foss_rec.foss_id) + '/list-videos-' + lang_obj.name + '.html'
            ctx = {'collection': list(tr_recs), 'foss_details': all_foss_details,
                   'foss': foss_rec.foss_id, 'lang': lang_obj.language_id}
            convert_template_to_html_file(archive, filepath, "tutorial_search.html", ctx)
            add_sheets(archive, foss_rec.foss_id, foss_rec.foss, lang_obj.name)
            # archive.close()

        # archive = open_archive_file(zip_file_name)

        if eng_flag:
            add_sheets(archive, foss_rec.foss_id, foss_rec.foss, eng_rec.name)

        # add common files for current foss
        add_common_files(archive, common_files)
        # archive.close()

    # archive = open_archive_file(zip_file_name)
    # add side-by-side tutorials for selected languages
    languages = add_side_by_side_tutorials(archive, languages)

    ctx = {'foss_details': all_foss_details, 'foss': foss_rec.id,
           'lang': eng_rec.id, 'languages': languages}
    convert_template_to_html_file(archive, 'spoken/videos/home.html', "home.html", ctx)

    # add all required static files to archive
    add_static_files(archive)
    archive.close()
    print 'Archive created successfully!'
    print 'Location:', zip_file_name

# start creating zip file
main()
