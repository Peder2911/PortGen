
import jinja2
import os
import markdown as md
import fire 
import yaml
from collections import defaultdict, namedtuple

color = lambda x,color: f"\x1b[{color}m"+x+"\x1b[0m"
yellow = lambda x: color(x,"33")
green = lambda x: color(x,"32")
blue = lambda x: color(x,"35")
purple = lambda x: color(x,"34")

Entry = namedtuple("Entry",("name","link"))

def markdownWithHeader(rawMd):
    lines = rawMd.split("\n")
    lines.reverse()

    yamllines = []
    if lines.pop() == "---":
        l = "" 
        while l != "---":
            yamllines += [l]
            l = lines.pop()

    lines.reverse()
    markdown = "\n".join(lines)
    markdown = md.markdown(markdown)

    if yamllines:
        headervalues = yaml.safe_load("\n".join(yamllines))
    else:
        headervalues = {}

    header = defaultdict(lambda: None)
    header.update(headervalues)
    return markdown,header 

def generate(to: str = "dist") -> None:
    print(purple(f"*** Emitting to {to} ***"))

    env = jinja2.Environment(
        loader = jinja2.FileSystemLoader("templates") 
    )

    fullPaths = lambda folder: [os.path.join(folder,p) for p in os.listdir(folder)]
    withExt = lambda paths,ext: [p for p in paths if os.path.splitext(p)[-1] == ext]
    fname = lambda fullpath: os.path.splitext(os.path.split(fullpath)[-1])[0]

    entries = []

    print(purple("Doing entries..."))
    for path in withExt(fullPaths("src"),".md"):
        name = fname(path)
        print("\t" + blue(name))
        entries.append(Entry(name=name.replace("_"," "),link=f"./{name}.html"))

        with open(path) as f:
            md,header = markdownWithHeader(f.read())
            if not header:
                print(yellow("No header"))

            t = env.get_template("entry.html")
            rnd = t.render(content=md,**header)

            with open(os.path.join(to,name+".html"),"w") as f:
                f.write(rnd)

    print(purple("Doing index..."))
    with open(os.path.join(to,"index.html"),"w") as f:
        t = env.get_template("index.html")
        rnd = t.render(entries=entries)
        f.write(rnd)
    
    print(green("Done! :)"))

if __name__ == "__main__":
    fire.Fire(generate)
