import argparse
import json
from digester import Digester
from graph_writer import GraphWriter
import tempfile

def parse_command_line_arguments():
        parser = argparse.ArgumentParser(description="Captures the message statistics for the provided queue manager.")

        #Positional required arguments
        parser.add_argument("input_dir", help="Location of captured statistics. Should only contain statistics snapshots from capture.")

        #Optional arguments
        parser.add_argument("-o", "--output", help="The directory to output the generated pdf to.")

        args = parser.parse_args()

        return args

if __name__ == '__main__':
        args = parse_command_line_arguments()
	
	digester = Digester()
	processed_stats = digester.process(args.input_dir)
	
	output_dir = args.output
	if not output_dir:
		output_dir = tempfile.mkdtemp()
	graph_writer = GraphWriter()
	pdf_loc = graph_writer.process(processed_stats, output_dir)

	print "Your pdf has been generated at %s" % pdf_loc
	
