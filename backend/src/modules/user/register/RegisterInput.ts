import { IsEmail, Length } from "class-validator";
import { Field, InputType } from "type-graphql";
import { IsEmailAlreadyExist } from "./isEmailAlreadyExist";

@InputType()
export class RegisterInput{
    @Field()
    @Length(1, 15, {message: "Invalid first name"})
    firstName: string;

    @Field()
    @Length(1, 15, {message: "Invalid last name"})
    lastName: string;

    @Field()
    @IsEmail()
    @IsEmailAlreadyExist({message: "email address already in use"})
    email: string;

    @Field()
    password: string;
}