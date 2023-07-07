import {
	registerDecorator,
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
} from 'class-validator';
import { DataService } from './data.service';
import { Injectable } from '@nestjs/common';

export function IsDataExistedByHashValue(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			name: 'isDataExisted',
			target: object.constructor,
			propertyName,
			options: validationOptions,
			validator: IsDataExistedByHashValueConstraint,
		});
	};
}

@Injectable()
@ValidatorConstraint({ async: true })
export class IsDataExistedByHashValueConstraint implements ValidatorConstraintInterface {
	constructor(private readonly connection: DataService) {}

	async validate(value: any): Promise<boolean> {
		const result = await this.createQueryBuilder(value);
		if (typeof result == 'boolean') {
			return result;
		}
		return false;
	}

	private async createQueryBuilder(value: any) {
		return await this.connection.findOneBy({ hashValue: value });
	}
}
