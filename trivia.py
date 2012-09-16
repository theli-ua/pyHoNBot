#!/usr/bin/env python
# (c) 2012 Ninja101
#
#
"""
"""

import pickle

if __name__ == '__main__':
	questions = pickle.load(open("triviadb", "r"))
	print(questions)
	while True:
		action = raw_input("Action: ")
		if action == "add":
			q = raw_input("Question: ")
			answer = raw_input("Answer: ")
			questions.append({"question": q, "answers": answer})
			pickle.dump(questions, open("triviadb", "w"))
		elif action == "remove":
			q = raw_input("Question: ")
			for i in range(len(questions)):
				if questions[i]['question'].lower() == q.lower():
					questions.pop(i)
			pickle.dump(questions, open("triviadb", "w"))
		elif action == "edit":
			pickle.dump(questions, open("triviadb", "w"))
		print("Done.")