from __future__ import annotations
from collections.abc import Iterable
import os
import csv
import random

import logging

class AnnotationProvider:

    def __init__(self, path: str, DEBUG: bool = False):
        """Initialize the annotation provider.

        Parameters
        ----------
        path : str
            Path to the annotation files.
            This directory should contain a file called 'uses.tsv' and 'instances.tsv'.
        DEBUG : bool, optional
            If set to True, the annotation provider will print debug messages, by default False

        Returns
        -------
        AnnotationProvider
            An annotation provider.

        Raises
        ------
        FileNotFoundError
            If the path does not exist, or if the path does not contain the required files.

        ValueError
            If the uses or instances file is not in the correct format.

        Example
        --------
        >>> annotation_provider = AnnotationProvider('example_annotator/annotations')
        """
        self._DEBUG = DEBUG
        if self._DEBUG:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self._path = path
        if not os.path.exists(self._path):
            if DEBUG:
                logging.warning(f"Path '{self._path}' does not exist.")
            raise FileNotFoundError(f"Path '{self._path}' does not exist.")
        if not os.path.exists(os.path.join(self._path, 'uses.tsv')):
            if DEBUG:
                logging.warning(f"Path '{self._path}' does not contain a uses file.")
            raise FileNotFoundError(f"Path '{self._path}' does not contain a 'uses.tsv' file.")
        if not os.path.exists(os.path.join(self._path, 'instances.tsv')):
            if DEBUG:
                logging.warning(f"Path '{self._path}' does not contain a instances file.")
            raise FileNotFoundError(f"Path '{self._path}' does not contain a 'instances.tsv' file.")
        
        if self._DEBUG:
            logging.debug(f"Loading uses file from '{self._path}'.")
        self._uses = self._load_uses()
        self._instances = self._load_instances()
        if self._DEBUG:
            logging.debug(f"Loaded {len(self._uses)} uses and {len(self._instances)} instances from path '{self._path}'.")
        
        self._judgements = [] 


    def _load_uses(self) -> dict[int, dict]:
        """Load the uses annotations.

        Returns
        -------
        dict[int, obj]
            A dictionary containing the uses annotations, indexed by their respective ids.

        Raises
        ------
        ValueError
            If the uses file is not in the correct format.


        Example
        -------
        The following example shows the expected format of the uses dict returned.
        {
            dataID: {
                'dataID': int,
                'context': str,
                'indices_target_token': [tuple(int, int)],
                'indices_target_sentence': [tuple(int, int)],
                'lemma': str,
            }
        }
        """
        uses = {}
        with open(os.path.join(self._path, 'uses.tsv'), 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['dataID'] in uses:
                    raise ValueError(f"Duplicate dataID '{row['dataID']}' in uses file.")
                uses[row['dataID']] = {
                    'dataID': row['dataID'],
                    'context': row['context'],
                    'indices_target_token': [tuple(int(i) for i in index.split(':')) for index in row['indices_target_token'].split(',')],
                    'indices_target_sentence': [tuple(int(i) for i in index.split(':')) for index in row['indices_target_sentence'].split(',')],
                    'lemma': row['lemma'],
                }
        return uses


    def _load_instances(self) -> dict[int, dict]:
        """Load the instances annotations.
        As the instance file depends on the annotation type, the function is implemented on a meta level,
        therefore the dictonary obj structure is dependend on the annotation type.

        Returns
        -------
        dict[int, obj]
            A dictionary containing the instances annotations, indexed by their respective ids.

        Raises
        ------
        ValueError
            If the instances file is not in the correct format.

        Example
        -------
        The following example shows the generated dictionary entries for use pairs.
        {
            instanceID: {
                'instanceID': int,
                'dataIDs': [int],
                'label_set': [str]|[int],
                'non_label': str,
            }
        }
        """
        instances = {}
        with open(os.path.join(self._path, 'instances.tsv'), 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                if row['instanceID'] in instances:
                    raise ValueError(f"Duplicate instanceID '{row['instanceID']}' in instances file.")
                instances[row['instanceID']] = row.copy()
                # Convert possible lists to lists
                for key in row.keys():
                    if len(row[key].split(',')) > 1:
                        # Check if the list is a list of ints
                        try:
                            instances[row['instanceID']][key] = [int(i) for i in row[key].split(',')]
                        except ValueError:
                            instances[row['instanceID']][key] = row[key].split(',')
                    
        return instances


    def get_use(self, index: int|None = None) -> dict:
        """Get the use for a given index. If no index is given, all uses are returned.
            
        Parameters
        ----------
        index : int, optional
            The index of the use, by default None.

        Returns
        -------
        dict
            The use or a dictionary containing all uses. 

        Raises
        ------
        ValueError
            If the index is not in the uses dict.

        Example
        -------
        >>> annotation_provider.get_use(0)
        {
            'dataID': 0,
            'context': 'The use of the word
            'indices_target_token': [(0, 3)],
            'indices_target_sentence': [(0, 3)],
            'lemma': 'use',
        }
        >>> annotation_provider.get_use()
        {
            0: {
                'dataID': 0,
                'context': 'The use of the word
                'indices_target_token': [(0, 3)],
                'indices_target_sentence': [(0, 3)],
                'lemma': 'use',
            },
            1: {
                ...
            },
            ...
        }
        """
        if index is None:
            return self._uses
        if index not in self._uses:
            raise ValueError(f"Index '{index}' not in uses dict.")
        return self._uses[index]


    def get_uses_ids(self) -> list:
        """Get a list of all uses ids.

        Returns
        -------
        list
            A list of all uses ids.

        Example
        -------
        >>> annotation_provider.get_uses_ids()
        [0, 1, 2, 3, ...]
        """
        return list(self._uses.keys())


    def get_uses_iterator(self, RANDOM: bool = False) -> Iterable:
        """Get an iterator over all usess.

        Parameters
        ----------
        RANDOM : bool, optional
            If the iterator should be shuffled, by default False

        Returns
        -------
        iter
            An iterator over all usess.

        Example
        -------
        >>> for uses in annotation_provider.get_uses_iterator():
        >>>     print(uses)
        {
            'dataID': 0,
            'context': 'The use of the word
            'indices_target_token': [(0, 3)],
            'indices_target_sentence': [(0, 3)],
            'lemma': 'use',
        }
        """
        if RANDOM:
            return iter([ self._uses[index] for index in random.sample(sorted(self._uses), len(self._uses)) ])
        return iter(self._uses.values())


    def get_instance(self, index: int|None = None) -> dict:
        """Get the instance for a given index. If no index is given, all instances are returned.
        Note: The instance dict is dependend on the annotation type.
            
        Parameters
        ----------
        index : int, optional
            The index of the instance, by default None

        Returns
        -------
        dict
            The instance or a dictionary containing all instance.

        Raises
        ------
        ValueError
            If the index is not in the instances dict.

        Example
        -------
        Example for use pairs.
        >>> annotation_provider.get_instance(0)
        {
            'instanceID': 0,
            'dataIDs': [0, 1],
            'label_set': ['use', 'uses'],
            'non_label': 'use',
        }
        >>> annotation_provider.get_instance()
        {
            0: {
                'instanceID': 0,
                'dataIDs': [0, 1],
                'label_set': ['use', 'uses'],
                'non_label': 'use',
            },
            1: {
                ...
            },
            ...
        }
        """
        if index is None:
            return self._instances
        if index not in self._instances:
            raise ValueError(f"Index '{index}' not in instances dict.")
        return self._instances[index]


    def get_instance_ids(self) -> list:
        """Get a list of all instance ids.

        Returns
        -------
        list
            A list of all instance ids.

        Example
        -------
        >>> annotation_provider.get_instance_ids()
        [0, 1, 2, 3, ...]
        """
        return list(self._instances.keys())

    
    def get_instances_iterator(self, RANDOM: bool = False) -> Iterable:
        """Get an iterator over all instances.
        Note: The instance dict is dependend on the annotation type.

        Parameters
        ----------
        RANDOM : bool, optional
            If the iterator should be shuffled, by default False

        Returns
        -------
        iter
            An iterator over all instances.

        Example
        -------
        >>> for instance in annotation_provider.get_instances_iterator():
        >>>     print(instance)
        {
            'instanceID': 0,
            'dataIDs': [0, 1],
            'label_set': ['use', 'uses'],
            'non_label': 'use',
        }
        """
        if RANDOM:
            return iter([ self._instances[index] for index in random.sample(sorted(self._instances), len(self._instances)) ])
        return iter(self._instances.values())


    def add_judgement(self, judgement: dict):
        """Add judgement to the judgement set.
        If the FLUSH flag is set, the judgement set is written to the judgement file.
        If a file called 'judgements.tsv' exists, the function appends to the existing file.

        Parameters
        ----------
        judgement : dict
            The judgement to add.

        Raises
        ------
        ValueError
            If the judgement is not valid.

        Example
        -------
        Simple Add:
        >>> judgement = {
        >>>     'instanceID': 0,
        >>>     'label': 'use',
        >>>     'comment': 'This is a comment.',
        >>> }
        >>> annotation_provider.add_judgement(judgement)
        """
        self._validate_judgement(judgement)
        self._judgements.append(judgement)


    def _validate_judgement(self, judgement: dict):
        """Validate a judgement.

        Parameters
        ----------
        judgement : dict
            The judgement to validate.

        Raises
        ------
        ValueError
            If the judgement is not valid.
        """
        if not isinstance(judgement, dict):
            if self._DEBUG:
                logging.warning(f"Judgement is not a dict: {judgement}")
            raise ValueError(f"Judgement '{judgement}' is not a dict.")
        if 'instanceID' not in judgement:
            if self._DEBUG:
                logging.warning(f"Judgement has no instanceID: {judgement}")
            raise ValueError(f"Judgement '{judgement}' does not contain the key 'instanceID'.")
        if 'label' not in judgement:
            if self._DEBUG:
                logging.warning(f"Judgement has no label: {judgement}")
            raise ValueError(f"Judgement '{judgement}' does not contain the key 'label'.")
        if 'comment' not in judgement:
            if self._DEBUG:
                logging.warning(f"Judgement has no comment: {judgement}")
            raise ValueError(f"Judgement '{judgement}' does not contain the key 'comment'.")
        if len(judgement) != 3:
            if self._DEBUG:
                logging.warning(f"Judgement has too many keys: {judgement}")
            raise ValueError(f"Judgement '{judgement}' has more than 3 keys.")


    def flush_judgement(self, path: str|None = None, filename: str = 'judgements.tsv'):
        """Write the judgement set to the judgement file.
        If a custom path is provided, the judgement file is written to this path, 
            else it is written to the path where the uses & instance file.
        If a file with the provided name exists, the function appends to the existing file.

        After the judgement set is written to the file, the judgement set is cleared.

        Parameters
        ----------
        path : str, optional
            The path to write the judgement file to, by default None
        filename : str, optional
            The name of the judgement file, by default 'judgements.tsv'

        Example
        -------
        For example, if the uses & instance file is located at 'data/uses.tsv' and 'data/instances.tsv',
        the judgement file is written to 'data/judgements.tsv'.
        >>> annotation_provider.add_judgement({
        >>>     'instanceID': 0,
        >>>     'label': '4',
        >>>     'comment': 'use',
        >>> })
        >>> annotation_provider.flush_judgement()

        If a custom path is provided, the judgement file is written to this path with the provided name.
        >>> annotation_provider.add_judgement({
        >>>     'instanceID': 0,
        >>>     'label': '4',
        >>>     'comment': 'use',
        >>> })
        >>> annotation_provider.flush_judgement(path='custom/path', filename='custom_judgements.tsv')
        """

        if self._DEBUG:
            logging.info(f"Writing judgements to path/file: '{path}/{filename}'")
        
        if path is None:
            path = self._path

        with open(os.path.join(path, filename), 'a+') as f:
            # Write Header if file is empty
            if os.stat(os.path.join(path, filename)).st_size == 0:
                f.write('instanceID\tlabel\tcomment\n')
            # Write Judgements
            for judgement in self._judgements:
                f.write(f"{judgement['instanceID']}\t{judgement['label']}\t{judgement['comment']}\n")
        
        self._judgements = []
