#!/usr/bin/env python3
"""
GitLab API 辅助脚本 - iShop GitLab Issue/MR 管理
使用标准库 urllib，无需安装额外依赖。

用法：
  python3 gitlab_api.py <命令> [参数...]

命令：
  user                              获取当前用户信息
  projects                          列出用户有权限的项目
  create_issue <project> <title> [--desc DESC] [--labels LABELS] [--assignee_id ID]
  create_branch <project> <branch> [--ref REF]
  create_mr <project> <source> <title> [--target TARGET] [--desc DESC] [--assignee_id ID]
  list_issues <project> [--state STATE] [--assignee_id ID]
  list_mrs <project> [--state STATE]
  merge_mr <project> <mr_iid>
  close_issue <project> <issue_iid>

环境：
  Token 获取优先级：git config --global gitlab.token > $GITLAB_TOKEN
  服务器：https://git.graspishop.com/
"""

import json
import sys
import subprocess
import urllib.request
import urllib.parse
import urllib.error

GITLAB_HOST = "https://git.graspishop.com"
API_BASE = f"{GITLAB_HOST}/api/v4"


def get_token():
    """获取 GitLab Token"""
    # 优先 git config
    try:
        result = subprocess.run(
            ["git", "config", "--global", "gitlab.token"],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    # 备选环境变量
    import os
    token = os.environ.get("GITLAB_TOKEN", "")
    if token:
        return token
    print("❌ 未找到 GitLab Token。请执行：git config --global gitlab.token <your-token>", file=sys.stderr)
    sys.exit(1)


def api_request(method, path, data=None):
    """发起 GitLab API 请求"""
    token = get_token()
    url = f"{API_BASE}{path}"
    headers = {
        "Private-Token": token,
        "Content-Type": "application/json"
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"❌ API 错误 {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)


def encode_project(project):
    """URL 编码项目路径"""
    return urllib.parse.quote(project, safe="")


# === 命令实现 ===

def cmd_user():
    """获取当前用户"""
    user = api_request("GET", "/user")
    print(json.dumps({"id": user["id"], "username": user["username"], "name": user["name"]}, ensure_ascii=False))


def cmd_projects():
    """列出项目"""
    projects = api_request("GET", "/projects?membership=true&per_page=100")
    result = []
    for p in projects:
        result.append({
            "id": p["id"],
            "path": p["path_with_namespace"],
            "name": p["name"],
            "description": p.get("description") or ""
        })
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_create_issue(args):
    """创建 Issue"""
    project = args[0]
    title = args[1]
    data = {"title": title}

    # 解析可选参数
    i = 2
    while i < len(args):
        if args[i] == "--desc" and i + 1 < len(args):
            data["description"] = args[i + 1]
            i += 2
        elif args[i] == "--labels" and i + 1 < len(args):
            data["labels"] = args[i + 1]
            i += 2
        elif args[i] == "--assignee_id" and i + 1 < len(args):
            data["assignee_ids"] = [int(args[i + 1])]
            i += 2
        else:
            i += 1

    path = encode_project(project)
    result = api_request("POST", f"/projects/{path}/issues", data)
    print(json.dumps({
        "iid": result["iid"],
        "title": result["title"],
        "web_url": result["web_url"]
    }, ensure_ascii=False))


def cmd_create_branch(args):
    """创建分支"""
    project = args[0]
    branch = args[1]
    ref = "main"

    i = 2
    while i < len(args):
        if args[i] == "--ref" and i + 1 < len(args):
            ref = args[i + 1]
            i += 2
        else:
            i += 1

    path = encode_project(project)
    data = {"branch": branch, "ref": ref}
    result = api_request("POST", f"/projects/{path}/repository/branches", data)
    print(json.dumps({"name": result["name"], "commit": result["commit"]["short_id"]}, ensure_ascii=False))


def cmd_create_mr(args):
    """创建 Merge Request"""
    project = args[0]
    source_branch = args[1]
    title = args[2]
    data = {
        "source_branch": source_branch,
        "target_branch": "main",
        "title": title,
        "remove_source_branch": True,
        "draft": True
    }

    i = 3
    while i < len(args):
        if args[i] == "--target" and i + 1 < len(args):
            data["target_branch"] = args[i + 1]
            i += 2
        elif args[i] == "--desc" and i + 1 < len(args):
            data["description"] = args[i + 1]
            i += 2
        elif args[i] == "--assignee_id" and i + 1 < len(args):
            data["assignee_ids"] = [int(args[i + 1])]
            i += 2
        else:
            i += 1

    path = encode_project(project)
    result = api_request("POST", f"/projects/{path}/merge_requests", data)
    print(json.dumps({
        "iid": result["iid"],
        "title": result["title"],
        "web_url": result["web_url"],
        "source_branch": result["source_branch"]
    }, ensure_ascii=False))


def cmd_list_issues(args):
    """列出 Issues"""
    project = args[0]
    params = "state=opened"

    i = 1
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            params = f"state={args[i + 1]}"
            i += 2
        elif args[i] == "--assignee_id" and i + 1 < len(args):
            params += f"&assignee_id={args[i + 1]}"
            i += 2
        else:
            i += 1

    path = encode_project(project)
    issues = api_request("GET", f"/projects/{path}/issues?{params}&per_page=20")
    result = [{"iid": i["iid"], "title": i["title"], "state": i["state"], "web_url": i["web_url"]} for i in issues]
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_list_mrs(args):
    """列出 MRs"""
    project = args[0]
    params = "state=opened"

    i = 1
    while i < len(args):
        if args[i] == "--state" and i + 1 < len(args):
            params = f"state={args[i + 1]}"
            i += 2
        else:
            i += 1

    path = encode_project(project)
    mrs = api_request("GET", f"/projects/{path}/merge_requests?{params}&per_page=20")
    result = [{"iid": m["iid"], "title": m["title"], "state": m["state"], "web_url": m["web_url"], "source_branch": m["source_branch"]} for m in mrs]
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_merge_mr(args):
    """合并 MR"""
    project = args[0]
    mr_iid = args[1]
    path = encode_project(project)
    data = {"should_remove_source_branch": True}
    result = api_request("PUT", f"/projects/{path}/merge_requests/{mr_iid}/merge", data)
    print(json.dumps({"state": result["state"], "merged_by": result.get("merged_by", {}).get("name", "")}, ensure_ascii=False))


def cmd_close_issue(args):
    """关闭 Issue"""
    project = args[0]
    issue_iid = args[1]
    path = encode_project(project)
    data = {"state_event": "close"}
    result = api_request("PUT", f"/projects/{path}/issues/{issue_iid}", data)
    print(json.dumps({"iid": result["iid"], "state": result["state"]}, ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "user": lambda: cmd_user(),
        "projects": lambda: cmd_projects(),
        "create_issue": lambda: cmd_create_issue(args),
        "create_branch": lambda: cmd_create_branch(args),
        "create_mr": lambda: cmd_create_mr(args),
        "list_issues": lambda: cmd_list_issues(args),
        "list_mrs": lambda: cmd_list_mrs(args),
        "merge_mr": lambda: cmd_merge_mr(args),
        "close_issue": lambda: cmd_close_issue(args),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"❌ 未知命令: {cmd}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
