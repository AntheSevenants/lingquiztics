def index_to_letter(index):
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    return alphabet[index]

def render_header(quiz_round, team_name):
    return f"```{{=latex}}\n\
\\begin{{tabularx}}{{\\textwidth}}{{c >{{\\raggedleft\\arraybackslash}}X}}\n\
\Huge {quiz_round} & \Large {team_name}\n\
\\end{{tabularx}}\n\
```\n\n"