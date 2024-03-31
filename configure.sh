dnf update -y
dnf install -y httpd 
echo "<h1>It works!</h1>" > /var/www/html/index.html
systemctl start httpd
systemctl enable httpd
systemctl is-enabled httpd