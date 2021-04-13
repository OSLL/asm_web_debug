# Function that replaces escape sequences with their "real" ASCII counterparts.
# Arguments:
#       in_str - string to replace escape sequences in.
__solid_esc_sqs = [['t', '\t'], ['n', '\n'], ['r', '\r'], ['"', '"']]
def solidify_esc_seq(in_str):
	for esc_seq in __solid_esc_sqs:
		in_str = in_str.replace("\\" + esc_seq[0], esc_seq[1])
	return in_str


# Function that turns a payload list of dictionaries into a single string.
# Arguments:
#       pl - payload list of dictionaries.
#       filters - list of tuples in a format of (stream, type) that tells the function
#                 to filter out only certain parts of response, corresponding to specified
#                 stream & type combinations.
def get_payload_str(pl, filters = [("stdout", "console")] ):
	out_str = ""
	for pl_el in pl:
		if "stream" in pl_el.keys() and "type" in pl_el.keys():
			for fl in filters:
				if fl[0] == pl_el["stream"] and fl[1] == pl_el["type"]\
				and "payload" in pl_el.keys():
					out_str += solidify_esc_seq(pl_el["payload"]
									.replace("\\\\", "\\"))
	return out_str

# Function that checks for presence of a certain pair in a payload list.
#       pl - payload list of dictionaries.
#       pair - pair tuple (ex. ("message", "thread-exited") for message: "thread-exited")
def is_in_payload(pl, pair):
	for pl_el in pl:
		if pair[0] in pl_el.keys() and pl_el[pair[0]] == pair[1]:
			return True
	return False
