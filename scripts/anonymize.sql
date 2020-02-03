drop table if exists auth_user_aa_aa_aa_aa_aa_aa_aa_aa_aa_aa;
create table auth_user_aa_aa_aa_aa_aa_aa_aa_aa_aa_aa (like auth_user including all);
insert into auth_user_aa_aa_aa_aa_aa_aa_aa_aa_aa_aa select * from auth_user;

