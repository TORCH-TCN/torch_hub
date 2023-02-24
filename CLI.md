# TORCH Hub CLI Quickstart

Create an institution: flask institutions create [NAME] [CODE]

List all institutions: flask institutions list

Delete an institution: flask institutions delete [ID]

Create a collection: flask collections create [INSTITUTION ID] [NAME] [CODE] (it will prompt you for the rest of the info)

List all collections in an institution: flask collections list [INSTITUTION ID]

Delete a collection: flask collections delete [COLLECTION ID]

Process & upload a specimen or multiple specimens: flask specimens process [COLLECTION ID] [PATH] (the path can be a single file or an entire directory)

List all specimens in a collection: flask specimens list [COLLECTION ID]

Delete a specimen: flask specimens delete [SPECIMEN ID]