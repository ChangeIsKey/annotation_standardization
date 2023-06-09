from optparse import OptionParser
import random
import logging

from annotation_provider import AnnotationProvider

def main(usage_dir, custom_dir, custom_filename, debug):

    if debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Debug mode is on.")

    if usage_dir is None:
        raise ValueError("usage_dir is None")
    if debug:
        logging.info(f"Using directory '{usage_dir}' for usage data.")
    
    if custom_dir is None:
        custom_dir = usage_dir
    if debug:
        logging.info(f"Using directory '{custom_dir}' to store judgements.")

    if custom_filename is None:
        custom_filename = "judgements.csv"
    if debug:
        logging.info(f"Using filename '{custom_filename}' to store judgements.")

    # Example annotator that randomly annotates the given set
    annotation_provider = AnnotationProvider(usage_dir, DEBUG=debug)
    for instance in annotation_provider.get_instances_iterator(RANDOM=True):
        print(f"Annotating instance: {instance}")
        # Randomly annotate the instance
        annotation_provider.add_judgement({'instanceID': instance['instanceID'], 'label':random.choice([*instance['label_set'], instance['non_label']]), 'comment': '-'})

    # Save the judgement
    annotation_provider.flush_judgement(path=custom_dir, filename=custom_filename)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--usage_dir", dest="usage_dir", help="Directory containing uses and instances data")
    parser.add_option("-c", "--custom_dir", dest="custom_dir", help="Directory to store custom judgements")
    parser.add_option("-f", "--custom_filename", dest="custom_filename", help="Filename to store custom judgements")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Enable debug mode")
    (options, args) = parser.parse_args()
    main(options.usage_dir, options.custom_dir, options.custom_filename, options.debug)