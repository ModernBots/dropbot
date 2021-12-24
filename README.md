<div align="center">
    <h1>ModernBot</h1>
    <a href="https://modernbot.t1c.dev/"><img src="assets/logo.svg" height="100"></a>
    <br>
    <h3>A minimalistic, modern Discord bot for roles and polls</h3>
    <a href="https://discord.com/api/oauth2/authorize?client_id=923845100277202974&permissions=1376805841984&scope=bot%20applications.commands" target="blank"><img src="https://shields.io/badge/invite_the-discord_bot-7289DA?logo=discord&style=for-the-badge" height="30"/></a>
</div>

### Technologies used
<a href="https://python.org"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png" height=20/></a> <a href="https://disnake.dev"><img src="https://disnake.dev/assets/disnake-logo.png" height=20/></a> <a href="https://python-pillow.org/"> <a href="https://github.com/mongodb/mongo-python-driver"><img src="https://cdn.discordapp.com/attachments/810799100940255260/923740541181624360/mongodb_logo_icon_170943.svg" height=20/></a> <a href="https://statcord.com"><img src="https://cdn.discordapp.com/attachments/810799100940255260/923742999542910976/ezgif-3-e69063bb05.png" height=20/></a> <a href="https://top.gg"><img src="https://blog.top.gg/favicon.png" height=20/></a> <a href="https://shields.io/"><img src="https://avatars.githubusercontent.com/u/6254238?s=200&v=4" height=20 /></a>

### Instructions

Type `/`, and navigate to ModernBot to see all the commands.

I have 2 main functions: polls and role menus.

For polls, you can use `/single_poll` to make a poll where everyone can vote only once, and `/multi_poll` to make a poll where everyone can vote one or more times.
Options should be seperated by commas, and a poll can have up to 25 options.
Example: `/single_poll title:What's your favorite fruit? options:Apple, Orange, Banana, Lime, Strawberry`
The poll author can use `/close_poll` to close a poll they made.

For role menus, you must have the **Manage Roles** permission in order to run the commands.
You can use `/single_role_menu` to make a role menu where everyone can only choose one role, and `/multi_role_menu` to make a role menu where everyone can choose one or more roles.
You have to choose one role when making a role menu, and can add more roles to a role menu by using `/add_role_to_menu`. Likewise you can use `/remove_role_from_menu` to remove a role from a menu.
