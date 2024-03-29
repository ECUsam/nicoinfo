# n站信息推送bot

## 指令列表
**需要管理员权限**

- **last `<user_uid>`** `--fast`  
  获取作者的最新投稿。  
  - `<user_uid>`: 作者的UID。
  - `--fast`: 选填参数。如果使用，则不发送封面。

- **sub `<user_uid>`**  
  订阅作者。
  - `<user_uid>`: 作者的UID。

- **desub `<user_uid>`**  
  取消订阅作者。
  - `<user_uid>`: 作者的UID。

- **list**  
  列出当前订阅。

## 关键字列表
**任何人都可以使用**

- **随机剧场**  
  随机发送剧场信息。

- **随机饼图**  
  随机发送一张饼图。

- **订阅tag `<n站tag>` `<生成的对应关键字>`**  
  订阅n站tag，订阅后发送关键字即可随机发送图片。
  - `<n站tag>`: N站的标签。
  - `<生成的对应关键字>`: 生成的关键字用于随机发送图片。

- **删除`<n站tag>`**  
  删除订阅的tag。需要先订阅才能起效。
  - `<n站tag>`: N站的标签。
