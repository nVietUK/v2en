import { Field, InputType, ObjectType } from '@nestjs/graphql';
import { User } from './user.entity';
import { Entity } from 'typeorm';
import { IsPasswordCorrent, IsUserNameExisted } from './user.validator';

@InputType('UserInput')
export class UserInput {
	constructor(
		username = '',
		familyName = '',
		givenName = '',
		gender = '',
		birthDay: Date = new Date(0, 0, 0),
	) {
		this.username = username;
		this.familyName = familyName;
		this.givenName = givenName;
		this.gender = gender;
		this.birthDay = birthDay;
	}

	@IsUserNameExisted({ message: 'username is existed' })
	@Field(() => String, { nullable: false })
	username: string;

	@Field(() => String, { nullable: false })
	familyName: string;

	@Field(() => String, { nullable: false })
	givenName: string;

	@Field(() => Date, { nullable: false })
	birthDay?: Date;

	@Field(() => String, { nullable: false })
	gender?: string;

	@IsPasswordCorrent({
		message:
			'The password must have the minimum length 8 with at leat a special character and more than 3 number',
	})
	@Field(() => String, { nullable: false })
	password?: string;
}

@Entity()
@ObjectType('UserOutput')
export class UserOutput {
	constructor(
		username = '',
		familyName = '',
		givenName = '',
		gender = '',
		birthDay: Date = new Date(0, 0, 0),
	) {
		this.username = username;
		this.familyName = familyName;
		this.givenName = givenName;
		this.gender = gender;
		this.birthDay = birthDay;
	}

	static fromUser(user: User) {
		return new UserOutput(
			user.username,
			user.familyName,
			user.givenName,
			user.gender,
			user.birthDay,
		);
	}

	@Field()
	username: string;

	@Field()
	familyName: string;

	@Field()
	givenName: string;

	@Field()
	gender: string;

	@Field()
	birthDay: Date;
}
