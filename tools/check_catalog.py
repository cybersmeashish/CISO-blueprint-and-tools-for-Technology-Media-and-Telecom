from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,re,urllib.parse
ROOT=Path(__file__).resolve().parents[1]
def check(output):
    output.mkdir(exist_ok=True,parents=True);m=json.loads((ROOT/"catalog/industry.json").read_text());sectors=m["sectors"]
    assert len(sectors)==len({s["folder"] for s in sectors})
    for s in sectors:
        folder=ROOT/s["folder"];assert folder.parent==ROOT and folder.is_dir() and (folder/"README.md").is_file()
    (output/"verification.json").write_text(json.dumps({"verification_in_progress":True})+"\n")
    links=0
    for p in ROOT.rglob("*.md"):
        if "evidence" in p.relative_to(ROOT).parts:continue
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)",p.read_text()):
            if target.startswith(("https://","http://","#","mailto:")):continue
            actual=p.parent/urllib.parse.unquote(target.split("#")[0]);assert actual.resolve().exists(),(p,target);links+=1
    migrations=[]
    for path in (ROOT/"migration").glob("*.json") if (ROOT/"migration").exists() else []:
        record=json.loads(path.read_text())
        for e in record["files"]:
            data=(ROOT/e["target_path"]).read_bytes();assert hashlib.sha256(data).hexdigest()==e["sha256"],e["target_path"]
        migrations.append({"source_repository":record["source_repository"],"source_commit":record["source_commit"],"target_folder":record["target_folder"],"original_files_byte_verified":len(record["files"])})
    files=[p for p in ROOT.rglob("*") if p.is_file() and "evidence" not in p.relative_to(ROOT).parts and "__pycache__" not in p.parts and p.suffix!=".pyc"]
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    (output/"source-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    record={"checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"repository":m["slug"],"industry":m["title"],"sector_folders":len(sectors),"folder_names":[s["folder"] for s in sectors],"local_links_checked":links,"source_files_hashed":len(files),"migrations":migrations,"runtime":{"python":platform.python_version(),"system":platform.system(),"machine":platform.machine()},"root_read_only":bool(os.statvfs("/").f_flag & os.ST_RDONLY),"workspace_read_only":bool(os.statvfs(str(ROOT)).f_flag & os.ST_RDONLY),"scope":"structure/link and migration byte checks; no sector-control, deployment or compliance tests"}
    (output/"verification.json").write_text(json.dumps(record,indent=2)+"\n");print(json.dumps(record,indent=2));return record
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args();check(a.output)
