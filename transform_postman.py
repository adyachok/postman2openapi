# Transforms Postman collection to OpenAPI v.3
# Checks for the latest Postman collection file and converts it to
# Swagger format.
import json
import os
from pathlib import Path

import yaml
from swagmanmock.parser.collection import Collection
from swagmanmock.spec import Spec
from swagmanmock import from_collection


def _get_postman_files():
    postman_files = Path().glob('MEDICOACH.postman_collection.json')
    postman_files = list(postman_files)
    postman_files.sort(key=os.path.getctime)
    return postman_files


def _get_collection(collection_file):
    collection = from_collection(collection_file)
    # Use only localhost mapping. My Postman collection has 'localhost' and
    # 'remote' folders, Swagmanmock does not work with collection sub folders.
    collection['item'] = collection['item'][0]['item']
    return collection


def _parse_examples(converted, to_yaml=False):
    if to_yaml:
        converted = yaml.load(converted, Loader=yaml.FullLoader)
    for k, v in converted['paths'].items():
        for k in v:
            if 'requestBody' in v[k]:
                content = v[k]['requestBody']['content']
                for kk in content.keys():
                    link = v[k]['requestBody']['content'][kk]
                    if 'example' in link:
                        example = link['example']
                        if 'value' in example:
                            link['example'] = json.loads(example['value'])
    return converted


def convert(to_yaml=True):
    postman_files = _get_postman_files()
    if not len(postman_files):
        print('Any Postman collection found. Exit...')
        return
    postman_file = postman_files[0]

    collection = Collection(_get_collection(postman_file))
    spec = Spec(collection)
    converted = _parse_examples(spec.convert(yaml=to_yaml), to_yaml=to_yaml)

    if to_yaml:
        outfile = Path('openapi.yml')
        yaml.dump(converted, stream=outfile.open('w'))
    else:
        outfile = Path('openapi.json')
        Path(outfile).write_text(json.dumps(converted), encoding='utf-8')


if __name__ == '__main__':
    convert()

