from jinja2 import Template, Environment, FileSystemLoader, escape
import json, os, re, plistlib

root = os.path.dirname(os.path.abspath(__file__))
templatesPath = os.path.join(root, 'templates')
env = Environment(loader=FileSystemLoader(templatesPath), trim_blocks=True, lstrip_blocks=True)
template = env.get_template('index.html')


try:
	packages = dict(plistlib.readPlist(os.path.join(root, "package_info.plist")))
	plistlib.writePlist(packages, os.path.join(root,"package_info.plist"))

	with open(os.path.join(root, "package_info.json"),"w") as f:
		f.write(json.dumps(packages, indent=4, sort_keys=True))
except:
	print ("package_info.plist not found")


for package in packages["Packages"]:
	packagePath = os.path.join(os.path.join(root, "depictions"), package.get("bundleid"))
	
	if not os.path.isdir(packagePath):
		os.mkdir(packagePath)
	
	title = package.get("title", 0)
	bundleid = package.get("bundleid", 0)
	description = re.sub(r'\s+', ' ', package.get("description"))
	changelog = package.get("changelog", 0)
	min_ios = package.get("min_ios", 0)
	max_ios = package.get("max_ios", 0)
	strict_range = package.get("strict_range", 0)
	debug = package.get("debug", 0)
	version = package.get("version", 0)
	last_updated = package.get("last_updated", 0)
	source = package.get("source", 0)
	
	
	try:
		sortedChangelog = sorted(changelog,reverse = True)
	except:
		sortedChangelog = None

	
	with open(os.path.join(packagePath, "index.html"), 'w') as f:
		f.write(template.render(
			title = title,
			bundleid = bundleid,
			description = description,
			changelog = changelog,
			sortedChangelog = sortedChangelog,
			min_ios = min_ios,
			max_ios = max_ios,
			strict_range = strict_range,
			debug = debug,
			last_updated = last_updated,
			version = version,
			source = source
		))
	print ("Generated {}/index.html".format(package.get("bundleid")))
	
	'''
	
	sileo_keys = ["headerImage", "tintColor"]
	
	with open(os.path.join(templatesPath, "sileo.json")) as json_file:  
		data = json.load(json_file)
		for key in sileo_keys:
			val = entry.get(key)
			if val:
				data[key] = val
		tabs = data["tabs"]
		for json_entry in tabs:
			tabname = json_entry["tabname"]
			if tabname == "Details":
				views = json_entry["views"]
				views[0]["markdown"] = description
				views[2]["text"] = "PoomSmart"
		if min_ios:
			support_versions = {
				"class": "DepictionSubheaderView",
				"useMargins": True,
				"title": "Compatiable with iOS %s to %s" % (min_ios, max_ios) if min_ios and max_ios else "Compatible with iOS %s +" % min_ios
			}
			views.insert(0, support_versions)
		if changes:
			changes_tab = {
				"tabname": "Latest Changes",
				"views": [],
				"class": "DepictionStackView"
			}
			views = changes_tab["views"]
			for change in changes:
				views.append({
					"class": "DepictionSubheaderView",
					"title": "Version %s" % change[0]
				})
				change_part = ""
				if isinstance(change[1], list):
					for c in change[1]:
						change_part += "<li>%s</li>" % c
					change_part = "<ul>%s</ul>" % change_part
				else:
					change_part = "<ul><li>%s</li></ul>" % change[1]
				views.append({
					"markdown": change_part,
					"useRawFormat": True,
					"class": "DepictionMarkdownView"
				})
				views.append({
					"class": "DepictionSeparatorView"
				})
			tabs.append(changes_tab)

	with open(sileo_output_path, 'w') as out_file:
		json.dump(data, out_file)
	print("Generated %s" % sileo_output_path)
	
	'''