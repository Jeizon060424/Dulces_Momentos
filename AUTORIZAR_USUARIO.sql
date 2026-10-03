-- Ejecuta esta línea en Supabase > SQL Editor por cada usuario autorizado.
-- Cambia el correo y deja las comillas simples.

insert into public.allowed_emails(email)
values ('TU_CORREO@EJEMPLO.COM')
on conflict (email) do nothing;
