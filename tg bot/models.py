from typing import List

class User:
    def __init__(self, name: str, username: str):
        self._name = name
        self._username = username

    def name(self) -> str:
        return self._name

    def username(self) -> str:
        return self._username

    def output(self) -> str:
        return f"Пользователь: {self._name} (@{self._username})"


class Comment:
    def __init__(self, user: User, text: str):
        self._user = user
        self._text = text

    def user(self) -> User:
        return self._user

    def text(self) -> str:
        return self._text

    def output(self) -> str:
        return f"💬 {self._user.name()} (@{self._user.username()}): {self._text}"


class News:
    def __init__(self, title: str, date_publish: str, description: str):
        self._title = title
        self._date_publish = date_publish
        self._description = description
        self._likes: List[str] = []
        self._comments: List[Comment] = []

    def title(self) -> str:
        return self._title

    def date_publish(self) -> str:
        return self._date_publish

    def description(self) -> str:
        return self._description

    def likes(self) -> List[str]:
        return self._likes

    def comments(self) -> List[Comment]:
        return self._comments

    def like(self, user: User) -> bool:
        if user.username() not in self._likes:
            self._likes.append(user.username())
            return True
        return False

    def add_comment(self, comment_obj: Comment) -> None:
        self._comments.append(comment_obj)

    def output(self) -> str:
        lines = [f"📰 *{self._title}*", f"📅 Дата: {self._date_publish}", f"📝 {self._description}"]
        
        if self._likes:
            lines.append(f"❤️ Лайки ({len(self._likes)}): {', '.join(self._likes)}")
        else:
            lines.append("❤️ Лайки: Нет")

        if self._comments:
            lines.append("\n*Комментарии:*")
            for c in self._comments:
                lines.append(c.output())
        else:
            lines.append("💬 Комментарии: Нет")
            
        return "\n".join(lines)


class Article(News):
    def __init__(self, title: str, date_publish: str, description: str, author: str, full_text: str):
        super().__init__(title, date_publish, description)
        self._author = author
        self._full_text = full_text

    def author(self) -> str:
        return self._author

    def full_text(self) -> str:
        return self._full_text

    def output(self) -> str:
        base_output = super().output()
        return f"{base_output}\n\n✍️ *Автор статьи:* {self._author}\n📜 *Полный текст:* {self._full_text}"