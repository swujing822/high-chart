function sendScheduledEmail() {
  var now = new Date();
  var timeString = Utilities.formatDate(now, "GMT+8", "yyyy-MM-dd HH:mm");

  var body = "每日任务更新！\n发送时间：" + timeString + "\n\n";
  body += "以下是你 Google Drive 的文件结构（含大小）：\n\n";

  var root = DriveApp.getRootFolder(); // 根目录
  var treeText = listFolderTree(root, "");

  body += treeText;

  MailApp.sendEmail({
    to: "beefree365@163.com",
    subject: "每日更新：" + timeString,
    body: body
  });
}

// 递归列出文件夹结构，包含文件大小
function listFolderTree(folder, indent) {
  var output = indent + "📁 " + folder.getName() + "\n";
  indent += "  ";

  var files = folder.getFiles();
  while (files.hasNext()) {
    var file = files.next();
    var sizeMB = (file.getSize() / (1024 * 1024)).toFixed(2); // 转换为 MB
    output += indent + "├─ " + file.getName() + " (" + sizeMB + " MB)\n";
  }

  var subFolders = folder.getFolders();
  while (subFolders.hasNext()) {
    var subFolder = subFolders.next();
    output += listFolderTree(subFolder, indent + "│ ");
  }

  return output;
}
