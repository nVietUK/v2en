import { Module } from '@nestjs/common';
import { UserService } from './user.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './user.entity';
import { UserResolver } from './user.resolver';
import { IsUserNameExistedConstraint } from './user.validator';

@Module({
	providers: [UserResolver, UserService, IsUserNameExistedConstraint],
	imports: [TypeOrmModule.forFeature([User])],
})
export class UserModule {}
