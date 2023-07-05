import { compare  } from "bcryptjs";
import { User } from "../../entity/User";
import { Arg, Ctx, Mutation, Resolver } from "type-graphql";
import { MyContext } from "src/types/MyContext";

@Resolver()
export class LoginResolver {
  @Mutation(() => User, { nullable: true })
  async login(
    @Arg("email") email: string,
    @Arg("password") password: string,
    @Ctx() context: MyContext
  ): Promise<User | null> {
    const user = await User.findOne({ where: { email: email } });
    if (!user) {
      return null;
    }
    
    const valid = await compare(password, user.password)
    if (!valid) {
      return null;
    }

    context.req.session!.userID = user.id

    return user;
  }
}
