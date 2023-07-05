import { hash } from "bcryptjs";
import { User } from "../../entity/User";
import { Arg, Mutation, Query, Resolver } from "type-graphql";
import { RegisterInput } from "./register/RegisterInput";

@Resolver()
export class RegisterResolver {
  @Query(() => String)
  async helloWord() {
    return "Hello world!";
  }

  @Mutation(() => User)
  async register(
    @Arg("data") { firstName, lastName, password, email }: RegisterInput
  ): Promise<User> {
    const hashedPassword = await hash(password, 12);

    const user = await User.create({
      firstName: firstName,
      lastName: lastName,
      email: email,
      password: hashedPassword,
    }).save();

    return user;
  }
}
