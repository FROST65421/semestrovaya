SELECT users.name, phones.number 
FROM users
JOIN userPhones ON users.id = userPhones.user_id
JOIN phones ON phones.id = userPhones.phone_id;