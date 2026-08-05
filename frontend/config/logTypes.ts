export interface LogTypeConfig {
  id: string;
  label: string;
  tier: "web" | "telephony" | "db";
  defaultPath: string;
}

export const LOG_TYPES: LogTypeConfig[] = [
  {
    id: "apache_error",
    label: "Apache Error Log",
    tier: "web",
    defaultPath: "/var/log/httpd/error.log",
  },
  {
    id: "apache_access",
    label: "Apache Access Log",
    tier: "web",
    defaultPath: "/var/log/httpd/access.log",
  },
  {
    id: "apache_app",
    label: "Apache Application Log",
    tier: "web",
    defaultPath: "/var/log/httpd/apache.log",
  },
  {
    id: "mysql",
    label: "MySQL Error Log",
    tier: "web",
    defaultPath: "/var/log/mysql/error.log",
  },
  {
    id: "laravel",
    label: "Laravel Log",
    tier: "web",
    defaultPath: "/var/www/html/storage/logs/laravel.log",
  },
];