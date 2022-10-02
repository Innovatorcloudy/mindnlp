# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
IWSLT2017 load function
"""
# pylint: disable=C0103

import os
from mindspore.dataset import IWSLT2017Dataset
from mindnlp.utils.download import cache_file
from mindnlp.dataset.register import load
from mindnlp.configs import DEFAULT_ROOT
from mindnlp.utils import untar

URL = "https://drive.google.com/u/0/uc?id=12ycYSzLIG253AFN35Y6qoyf9wtkOjakp&confirm=t"

MD5 = "aca701032b1c4411afc4d9fa367796ba"


SUPPORTED_DATASETS = {
    "valid_test": ["dev2010", "tst2010"],
    "language_pair": {
        "en": ["nl", "de", "it", "ro"],
        "ro": ["de", "en", "nl", "it"],
        "de": ["ro", "en", "nl", "it"],
        "it": ["en", "nl", "de", "ro"],
        "nl": ["de", "en", "it", "ro"],
    },
    "year": 17,
}


@load.register
def IWSLT2017(root=DEFAULT_ROOT, split=("train", "valid", "test"), language_pair=("de", "en")):
    r"""
    Load the IWSLT2017 dataset

    The available datasets include following:

    **Language pairs**:

    +-----+-----+-----+-----+-----+-----+
    |     |"en" |"nl" |"de" |"it" |"ro" |
    +-----+-----+-----+-----+-----+-----+
    |"en" |     |   x |  x  |  x  |  x  |
    +-----+-----+-----+-----+-----+-----+
    |"nl" |  x  |     |  x  |  x  |  x  |
    +-----+-----+-----+-----+-----+-----+
    |"de" |  x  |   x |     |  x  |  x  |
    +-----+-----+-----+-----+-----+-----+
    |"it" |  x  |   x |  x  |     |  x  |
    +-----+-----+-----+-----+-----+-----+
    |"ro" |  x  |   x |  x  |  x  |     |
    +-----+-----+-----+-----+-----+-----+

    Args:
        root (str): Directory where the datasets are saved. Default: "~/.mindnlp"
        split (str|Tuple[str]): Split or splits to be returned.
            Default:('train', 'valid', 'test').
        language_pair (Tuple[str]): Tuple containing src and tgt language. Default: ('de', 'en').

    Returns:
        - **datasets_list** (list) -A list of loaded datasets.
            If only one type of dataset is specified,such as 'trian',
            this dataset is returned instead of a list of datasets.

    Raises:
        TypeError: If `root` is not a string.
        TypeError: If `split` is not a string or Tuple[str].
        TypeError: If `language_pair` is not a Tuple[str].
        RuntimeError: If the length of `language_pair` is not 2.
        RuntimeError: If `language_pair` is not in the range of supported datasets.

    Examples:
        >>> root = "~/.mindnlp"
        >>> split = ('train', 'valid', 'test')
        >>> language_pair = ('de', 'en')
        >>> dataset_train, dataset_valid, dataset_test = IWSLT2017(root, split, language_pair)
        >>> train_iter = dataset_train.create_dict_iterator()
        >>> print(next(train_iter))
        {'text': Tensor(shape=[], dtype=String, value= 'Vielen Dank, Chris.'),
        'translation': Tensor(shape=[], dtype=String, value= 'Thank you so much, Chris.')}

    """

    if not isinstance(language_pair, list) and not isinstance(language_pair, tuple):
        raise ValueError(f"language_pair must be list or tuple but got \
            {type(language_pair)} instead")

    assert len(language_pair) == 2, \
        "language_pair must contain only 2 elements: src and tgt language respectively"
    src_language, tgt_language = language_pair[0], language_pair[1]
    if src_language not in SUPPORTED_DATASETS["language_pair"]:
        raise ValueError(
            f"src_language '{src_language}' is not valid. Supported source languages are \
                {list(SUPPORTED_DATASETS['language_pair'])}"
            )
    if tgt_language not in SUPPORTED_DATASETS["language_pair"][src_language]:
        raise ValueError(
            f"tgt_language '{tgt_language}' is not valid for give src_language '\
                {src_language}'. Supported target language are \
                    {SUPPORTED_DATASETS['language_pair'][src_language]}"
        )
    if isinstance(split, str):
        split = split.split()

    cache_dir = os.path.join(root, "datasets", "IWSLT2017")
    file_path, _ = cache_file(None, cache_dir=cache_dir, url=URL, md5sum=MD5,
                              download_file_name="2017-01-trnmted.tgz")
    dataset_dir_name = untar(file_path, os.path.dirname(file_path))[0]
    dataset_dir_path = os.path.join(cache_dir, dataset_dir_name)
    untar_flie_name = "DeEnItNlRo-DeEnItNlRo.tgz"
    untar_file_path = os.path.join(dataset_dir_path, 'texts',
                                   'DeEnItNlRo', 'DeEnItNlRo', untar_flie_name)
    untar(untar_file_path, os.path.dirname(untar_file_path))
    datasets_list = []
    for usage in split:
        dataset = IWSLT2017Dataset(
            dataset_dir=dataset_dir_path, usage=usage, shuffle=False)
        datasets_list.append(dataset)
    if len(datasets_list) == 1:
        return datasets_list[0]
    return datasets_list